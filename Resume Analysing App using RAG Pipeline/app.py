import streamlit as st
import os
import tempfile
from backend import ResumeAnalyzer, SAMPLE_JOB_DESCRIPTIONS
import pandas as pd
import plotly.graph_objects as go
from PIL import Image
import base64

# Initialize analyzer
analyzer = ResumeAnalyzer()

# Page config
st.set_page_config(
    page_title="Resume Analyzer Pro",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .match-score {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .high-match {
        background-color: #d4edda;
        color: #155724;
    }
    .medium-match {
        background-color: #fff3cd;
        color: #856404;
    }
    .low-match {
        background-color: #f8d7da;
        color: #721c24;
    }
    .suggestion-card {
        background-color: #2d3748;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 5px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)

# App logo/title
col1, col2 = st.columns([1, 5])
with col1:
    # Create a simple logo using emojis and styling
    st.markdown("""
        <div style="font-size: 3rem; font-weight: bold; color: #4CAF50;">📄</div>
        """, unsafe_allow_html=True)

with col2:
    st.title("Resume Analyzer Pro")
    st.markdown("### AI-Powered Resume Analysis and Career Guidance")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Upload Resume", "Job Matching", "Chat with Resume", "About"])

# Initialize session state
if 'uploaded_resume' not in st.session_state:
    st.session_state.uploaded_resume = None
    st.session_state.resume_text = ""
    st.session_state.resume_id = None
    st.session_state.analysis_results = None

if page == "Upload Resume":
    st.header("📤 Upload Your Resume")
    st.markdown("Upload your resume in PDF format to get started with analysis.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Process resume
        with st.spinner("Processing your resume..."):
            result = analyzer.process_resume(tmp_file_path, f"USER_{uploaded_file.name.split('.')[0]}")
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        if result:
            st.session_state.uploaded_resume = uploaded_file
            st.session_state.resume_text = result["text"]
            st.session_state.resume_id = result["resume_id"]
            st.session_state.entities = result["entities"]
            
            st.success("✅ Resume processed successfully!")
            
            # Display resume info
            st.subheader("Resume Information Extracted")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Skills Detected", len(st.session_state.entities.get("skills", [])))
            
            with col2:
                st.metric("Organizations", len(st.session_state.entities.get("organizations", [])))
            
            with col3:
                st.metric("Chunks Created", result["chunk_count"])
            
            # Show extracted entities
            # Show extracted entities
            with st.expander("View Extracted Entities"):
                st.write("### Skills")
                st.write(", ".join(st.session_state.entities.get("skills", ["None detected"])) or "None detected")
                
                st.write("### Organizations")
                st.write(", ".join(st.session_state.entities.get("organizations", ["None detected"])) or "None detected")
                
                st.write("### Locations")
                st.write(", ".join(st.session_state.entities.get("locations", ["None detected"])) or "None detected")
                
                # 👇 Projects display - now with proper titles and formatting
                st.write("### Projects")
                projects = st.session_state.entities.get("projects", [])
                project_descriptions = st.session_state.entities.get("project_descriptions", {})
                
                if projects:
                    for project in projects:
                        # Display project title in its original casing (should now be correct)
                        st.markdown(f"#### 🚀 {project}")
                        descriptions = project_descriptions.get(project, [])
                        if descriptions:
                            for desc in descriptions:
                                if desc.strip():  # Only display non-empty descriptions
                                    st.markdown(f"• {desc}")
                        else:
                            st.markdown("_No description available_")
                        st.markdown("---")
                else:
                    st.write("No projects detected")
                
                st.write("### Certifications")
                certifications = st.session_state.entities.get("certifications", [])
                if certifications:
                    for cert in certifications:
                        st.markdown(f"📜 {cert}")
                else:
                    st.write("No certifications detected")
        else:
            st.error("❌ Error processing resume. Please try again with a different file.")

elif page == "Job Matching":
    st.header("🎯 Job Description Matching")
    st.markdown("Select a job description or paste your own to see how well your resume matches.")
    
    if not st.session_state.resume_text:
        st.warning("Please upload a resume first in the 'Upload Resume' section.")
    else:
        # Job description selection
        job_option = st.selectbox(
            "Choose a sample job description or enter your own:",
            ["Select a sample..."] + list(SAMPLE_JOB_DESCRIPTIONS.keys()) + ["Enter custom job description"]
        )
        
        job_description = ""
        if job_option == "Enter custom job description":
            job_description = st.text_area("Paste your job description here:", height=300)
        elif job_option != "Select a sample...":
            job_description = SAMPLE_JOB_DESCRIPTIONS[job_option]
            st.text_area("Job Description", job_description, height=300, disabled=True)
        
        if job_description and st.button("Analyze Match"):
            with st.spinner("Analyzing resume match..."):
                analysis = analyzer.analyze_resume_job_match(st.session_state.resume_text, job_description)
                st.session_state.analysis_results = analysis
            
            if st.session_state.analysis_results:
                results = st.session_state.analysis_results
                
                # Display overall match score
                score = results["overall_match_percentage"]
                if score >= 80:
                    score_class = "high-match"
                    message = "Excellent Match!"
                elif score >= 60:
                    score_class = "medium-match"
                    message = "Good Match"
                else:
                    score_class = "low-match"
                    message = "Needs Improvement"
                
                st.markdown(f"""
                    <div class="match-score {score_class}">
                        {score}% - {message}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Create radar chart for match components
                categories = ['Overall', 'Skills', 'Experience', 'Education']
                values = [
                    results["overall_match_percentage"],
                    results["skills_match"]["percentage"],
                    results["experience_match"]["percentage"],
                    results["education_match"]["percentage"]
                ]
                
                fig = go.Figure(data=go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    line=dict(color='#4CAF50'),
                    marker=dict(size=10)
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=False,
                    title="Match Analysis by Category",
                    width=500,
                    height=500
                )
                
                st.plotly_chart(fig)
                
                # Detailed breakdown
                st.subheader("Detailed Analysis")
                
                # Skills match
                st.markdown("### 🔧 Skills Match")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Skills Match", f"{results['skills_match']['percentage']}%", 
                             f"{len(results['skills_match']['matched_skills'])} of {len(results['skills_match']['required_skills'])} skills matched")
                
                with col2:
                    if results['skills_match']['missing_skills']:
                        st.warning(f"Missing {len(results['skills_match']['missing_skills'])} skills")
                
                if results['skills_match']['required_skills']:
                    st.markdown("**Required Skills:**")
                    st.write(", ".join(results['skills_match']['required_skills']))
                
                if results['skills_match']['matched_skills']:
                    st.markdown("**✅ Your Matching Skills:**")
                    st.write(", ".join(results['skills_match']['matched_skills']))
                
                if results['skills_match']['missing_skills']:
                    st.markdown("**❌ Missing Skills:**")
                    st.write(", ".join(results['skills_match']['missing_skills']))
                
                # Experience match
                st.markdown("### 💼 Experience Match")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Experience Match", f"{results['experience_match']['percentage']}%")
                
                st.markdown(f"**Required Experience:** {results['experience_match']['required_experience']} years")
                st.markdown(f"**Your Experience:** {results['experience_match']['resume_experience']} years")
                
                # Education match
                st.markdown("### 🎓 Education Match")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Education Match", f"{results['education_match']['percentage']}%")
                
                st.markdown(f"**Required Education:** {results['education_match']['required_education']}")
                st.markdown(f"**Your Education:** {results['education_match']['resume_education']}")
                
                # Improvement suggestions
                st.markdown("### 💡 Improvement Suggestions")
                for suggestion in results["improvement_suggestions"]:
                    st.markdown(f"""
                        <div class="suggestion-card">
                            <strong>➤</strong> {suggestion}
                        </div>
                        """, unsafe_allow_html=True)

elif page == "Chat with Resume":
    st.header("💬 Chat with Your Resume")
    st.markdown("Ask questions about your resume or get career advice based on your profile.")
    
    if not st.session_state.resume_text:
        st.warning("Please upload a resume first in the 'Upload Resume' section.")
    else:
        # Display chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Job description context (optional)
        st.markdown("### Optional: Provide a Job Description for Context")
        job_option = st.selectbox(
            "Choose a sample job description or enter your own:",
            ["None"] + list(SAMPLE_JOB_DESCRIPTIONS.keys()) + ["Enter custom job description"],
            key="chat_job_option"
        )
        
        chat_job_description = ""
        if job_option == "Enter custom job description":
            chat_job_description = st.text_area("Paste job description:", height=100, key="chat_job_desc")
        elif job_option != "None":
            chat_job_description = SAMPLE_JOB_DESCRIPTIONS[job_option]
        
        # Chat interface
        st.markdown("### Ask Questions")
        user_question = st.text_input("Type your question here:", 
                                    placeholder="E.g., What skills should I learn? How can I improve my resume? What projects should I build?")
        
        if st.button("Ask") and user_question:
            with st.spinner("Thinking..."):
                response = analyzer.chat_with_resume(
                    st.session_state.resume_text, 
                    user_question, 
                    chat_job_description if chat_job_description else None
                )
            
            # Add to chat history
            st.session_state.chat_history.append({
                "question": user_question,
                "response": response
            })
        
        # Display chat history
        if st.session_state.chat_history:
            st.markdown("### Chat History")
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                st.markdown(f"""
                    <div style="background-color: #2d3748; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                        <strong>👤 You:</strong> {chat['question']}
                    </div>
                    <div style="background-color: #2d3748; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 5px solid #1890ff;">
                        <strong>🤖 Assistant:</strong> {chat['response']}
                    </div>
                    """, unsafe_allow_html=True)

elif page == "About":
    st.header("ℹ️ About Resume Analyzer Pro")
    st.markdown("""
    ### Welcome to Resume Analyzer Pro!
    
    This AI-powered application helps you analyze your resume against job descriptions and provides personalized recommendations to improve your career prospects.
    
    ### Features:
    - **Resume Processing**: Upload your PDF resume and extract key information
    - **Job Matching**: Compare your resume against job descriptions to get a match percentage
    - **Chat with Resume**: Ask questions about your resume and get personalized career advice
    - **Improvement Suggestions**: Get specific recommendations on skills, projects, and certifications
    
    ### Technology Stack:
    - **RAG Pipeline**: Retrieval-Augmented Generation for intelligent responses
    - **FAISS**: Efficient similarity search for resume chunks
    - **Hugging Face**: NER model (dslim/bert-base-NER) for entity extraction
    - **Sentence Transformers**: For semantic embeddings
    - **Streamlit**: Interactive web interface
    
    ### How It Works:
    1. Upload your resume in PDF format
    2. The system processes and analyzes your resume
    3. Compare against job descriptions to see match percentages
    4. Chat with your resume to get personalized career advice
    
    ### Privacy Notice:
    Your resume data is processed locally and stored only for your session. We do not share your personal information with third parties.
    
    ### Contact:
    For support or feedback, please contact: garvchangrani1@gmail.com
    """)
    
    # Show sample job descriptions
    st.markdown("### Sample Job Descriptions Available:")
    for job_title in SAMPLE_JOB_DESCRIPTIONS.keys():
        st.markdown(f"- {job_title}")

# Footer
st.markdown("---")
st.markdown("Resume Analyzer Pro © 2025 | Powered by AI and Machine Learning")

# Add some spacing
st.markdown("<br><br>", unsafe_allow_html=True)