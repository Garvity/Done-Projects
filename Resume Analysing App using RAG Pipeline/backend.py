import os
import PyPDF2
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import re
from typing import List, Dict, Tuple
import torch
import pdfplumber

# Initialize models
encoder = SentenceTransformer('all-MiniLM-L6-v2')

class ResumeAnalyzer:
    def __init__(self, vectorstore_dir="vectorstore"):
        self.vectorstore_dir = vectorstore_dir
        self.index = None
        self.chunks_data = []
        self.ner_pipeline = None
        self.load_vectorstore()
        self.load_ner_model()
    
    def load_ner_model(self):
        """Load Hugging Face NER model"""
        try:
            tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER",token=False)
            model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER",token=False)
            self.ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
            print("NER model loaded successfully")
        except Exception as e:
            print(f"Error loading NER model: {e}")
    
    def load_vectorstore(self):
        """Load FAISS index and chunks data"""
        try:
            index_path = os.path.join(self.vectorstore_dir, "resume_index.faiss")
            data_path = os.path.join(self.vectorstore_dir, "chunks_data.pkl")
            
            if os.path.exists(index_path) and os.path.exists(data_path):
                self.index = faiss.read_index(index_path)
                with open(data_path, 'rb') as f:
                    self.chunks_data = pickle.load(f)
                print("Vectorstore loaded successfully")
            else:
                print("Vectorstore not found. Please run data_pipeline.py first.")
        except Exception as e:
            print(f"Error loading vectorstore: {e}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF resume using pdfplumber with cleanup of PDF artifacts"""
        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text(
                        x_tolerance=3,
                        y_tolerance=3,
                        layout=True,
                        keep_blank_chars=True
                    )
                    if text:
                        full_text += text + "\n\n"
            
            # Clean up PDF artifacts
            # Replace (cid:18) with a standard arrow or bullet
            full_text = re.sub(r'\(cid:\d+\)', '→', full_text)  # Replace all cid codes with arrow
            
            # Clean up extra whitespace and fix common issues
            full_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', full_text)
            full_text = re.sub(r'•\s*Developedafull', '• Developed a full', full_text)  # Fix concatenated words
            full_text = full_text.strip()
            
            if not full_text:
                print("Warning: No text extracted from PDF.")
                return ""
            
            return full_text
            
        except Exception as e:
            print(f"Error extracting text from PDF with pdfplumber: {e}")
            try:
                print("Falling back to PyPDF2...")
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
                    return text.strip()
            except Exception as e2:
                print(f"PyPDF2 also failed: {e2}")
                return ""
    
    def recursive_chunking(self, text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Recursively chunk text with overlap"""
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a natural break
            cut_point = end
            for i in range(end, start, -1):
                if i < len(text) - 1 and text[i] in '.!?\n':
                    cut_point = i + 1
                    break
            
            chunk = text[start:cut_point]
            chunks.append(chunk)
            
            start = cut_point - overlap
            if start < 0:
                start = 0
        
        return chunks
        
    def extract_entities(self, text: str) -> Dict:
        """Extract resume-specific entities using rules and keyword matching (more accurate than generic NER)"""
        try:
            entities = {
                "skills": [],
                "organizations": [],
                "locations": [],
                "certifications": [],
                "education_institutions": [],
                "projects": [],
                "persons": []
            }
            
            # Clean and normalize text
            text_lower = text.lower()
            
            # 1. Extract PERSON NAME (heuristic: first 1-3 lines often contain name)
            lines = text.split('\n')
            if len(lines) > 0:
                # Look for name in first few lines (skip lines with emails, phones, symbols)
                for i in range(min(5, len(lines))):
                    line = lines[i].strip()
                    # Skip lines with obvious non-name content
                    if not line or any(x in line.lower() for x in ['@', '+91', 'http', 'www', 'linkedin', 'github', '§', 'ï', '#', 'h+']):
                        continue
                    # If line has 2-3 words and starts with capital letters, likely a name
                    words = line.split()
                    if 2 <= len(words) <= 4:
                        if all(len(w) > 1 and w[0].isupper() for w in words if len(w) > 0):
                            entities["persons"].append(line.strip())
                            break
            
            # 2. Extract SKILLS (look for "Skills" section or common skill keywords)
            skills_section_patterns = [
                r'skills\s*[:\-]?\s*(.*?)(?:\n\s*\n|\Z)',
                r'technical\s+skills\s*[:\-]?\s*(.*?)(?:\n\s*\n|\Z)',
                r'proficient\s+in\s*[:\-]?\s*(.*?)(?:\n\s*\n|\Z)',
            ]
            
            found_skills = set()
            
            # First, try to find skills section
            for pattern in skills_section_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    skills_text = match.group(1)
                    # Split by commas, semicolons, or bullets
                    skill_items = re.split(r'[,;•\-\n]', skills_text)
                    for item in skill_items:
                        item = item.strip().strip('•').strip()
                        if len(item) > 2 and not item.lower().startswith(('http', 'www')):
                            # Clean up common resume bullet point artifacts
                            item = re.sub(r'^[\s\d\.\)\-]+', '', item)
                            if len(item) > 2:
                                found_skills.add(item)
            
            # If no skills section found, use keyword matching
            if not found_skills:
                # Common technical skills
                tech_skills = [
                    "python", "java", "javascript", "react", "node.js", "express", "django", "flask", 
                    "mongodb", "sql", "postgresql", "mysql", "aws", "azure", "gcp", "docker", "kubernetes",
                    "git", "github", "linux", "html", "css", "tailwind", "bootstrap", "tensorflow", 
                    "pytorch", "scikit-learn", "pandas", "numpy", "opencv", "mtcnn", "vgg16", "rest", 
                    "api", "jwt", "stripe", "react.js", "flask", "pytorch", "machine learning", "deep learning",
                    "data structures", "algorithms", "oops", "dbms", "operating system", "cloud", "full stack"
                ]
                
                for skill in tech_skills:
                    if skill in text_lower:
                        # Try to extract the exact casing from original text
                        start_idx = text_lower.find(skill)
                        if start_idx != -1:
                            exact_skill = text[start_idx:start_idx + len(skill)]
                            found_skills.add(exact_skill.title() if len(skill) <= 3 else exact_skill)
            
            entities["skills"] = list(found_skills)
            
            # 3. Extract ORGANIZATIONS (companies, colleges, institutes)
            org_patterns = [
                r'(?:intern|worked|developer|engineer)\s+at\s+([A-Za-z\s&]+)',
                r'(?:company|organization)[:\s]+([A-Za-z\s&]+)',
                r'([A-Za-z\s&]+)\s+(?:intern|job|position)',
            ]
            
            # Known organizations from resume context
            known_orgs = [
                "vit", "vit-ap", "narayana", "narayana college", "amazon", "aws", 
                "coursera", "ibm", "adobe", "mern", "next gen cloud"
            ]
            
            found_orgs = set()
            
            # Look for known organizations
            for org in known_orgs:
                if org in text_lower:
                    # Find exact match in original text
                    start_idx = text_lower.find(org)
                    if start_idx != -1:
                        exact_org = text[start_idx:start_idx + len(org)]
                        found_orgs.add(exact_org.title())
            
            # Look for organizations in education section
            edu_match = re.search(r'education.*?(?:\n\s*\n|\Z)', text, re.IGNORECASE | re.DOTALL)
            if edu_match:
                edu_text = edu_match.group(0)
                # Look for institution names after years
                year_pattern = r'(?:19|20)\d{2}.*?([A-Za-z\s\-&]+(?:college|university|institute|school|vit|narayana))'
                edu_orgs = re.findall(year_pattern, edu_text, re.IGNORECASE)
                for org in edu_orgs:
                    org = org.strip()
                    if len(org) > 3:
                        found_orgs.add(org.title())
            
            entities["organizations"] = list(found_orgs)
            entities["education_institutions"] = list(found_orgs)  # Also store as education institutions
            
            # 4. Extract CERTIFICATIONS
            cert_patterns = [
                r'certifications?\s*[:\-]?\s*(.*?)(?:\n\s*\n|\Z)',
                r'(?:certified|certificate)\s+(?:in|for|as)\s+([A-Za-z\s]+)',
                r'([A-Za-z\s]+)\s+certification',
                r'(?:aws|ibm|coursera|google|adobe)\s+certified',
            ]
            
            found_certs = set()
            
            for pattern in cert_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    match = match.strip()
                    if len(match) > 5 and not any(x in match.lower() for x in ['http', 'www', '@']):
                        found_certs.add(match.title())
            
            # Also look for specific known certifications
            known_certs = [
                "aws certified cloud practitioner", "clf-c02", "supervised machine learning", 
                "regression and classification", "machine learning with python"
            ]
            
            for cert in known_certs:
                if cert in text_lower:
                    start_idx = text_lower.find(cert)
                    if start_idx != -1:
                        exact_cert = text[start_idx:start_idx + len(cert)]
                        found_certs.add(exact_cert.title())
            
            entities["certifications"] = list(found_certs)
            
            # 5. Extract LOCATIONS (look for common location indicators)
            location_indicators = [
                "location:", "based in", "address:", "from", "residing in"
            ]
            
            found_locations = set()
            
            for indicator in location_indicators:
                if indicator in text_lower:
                    start_idx = text_lower.find(indicator) + len(indicator)
                    # Extract next 20-30 characters
                    location_text = text[start_idx:start_idx + 30]
                    # Clean it up
                    location_text = re.split(r'[\n,;]', location_text)[0].strip()
                    if len(location_text) > 2:
                        found_locations.add(location_text.title())
            
            # If no locations found, check for common Indian cities/states (since phone starts with +91)
            if not found_locations:
                indian_locations = [
                    "andhra pradesh", "telangana", "hyderabad", "vizag", "vijayawada", "amaravati",
                    "bangalore", "chennai", "mumbai", "delhi", "kolkata", "pune", "india"
                ]
                for loc in indian_locations:
                    if loc in text_lower:
                        found_locations.add(loc.title())
            
            entities["locations"] = list(found_locations) if found_locations else ["Not specified"]
            
            # 6. Extract PROJECTS with descriptions (robust multi-project parser)
            # 6. Extract PROJECTS with descriptions (handles bullet-pointed titles)
            found_projects = []
            project_descriptions = {}

            lines = text.split('\n')
            in_projects_section = False
            current_project = None
            current_description = []

            end_section_headers = [
                "internship", "experience", "skills", "certifications", 
                "education", "extracurricular", "achievements", "contact"
            ]

            i = 0
            while i < len(lines):
                original_line = lines[i]
                line = original_line.strip()
                if not line:
                    i += 1
                    continue

                # Check if entering Projects section
                if re.search(r'^\s*projects\s*[:\-]?\s*$', line, re.IGNORECASE):
                    in_projects_section = True
                    i += 1
                    continue

                # Check if leaving Projects section
                if in_projects_section:
                    for header in end_section_headers:
                        if re.search(rf'^\s*{header}\s*[:\-]?\s*$', line, re.IGNORECASE):
                            in_projects_section = False
                            if current_project:
                                project_descriptions[current_project] = current_description
                                found_projects.append(current_project)
                                current_project = None
                                current_description = []
                            break

                if not in_projects_section:
                    i += 1
                    continue

                # Handle project title that might be prefixed with bullet
                # Pattern: "• Project Name → Link" or "Project Name → Link"
                project_link_pattern = r'^(?:•\s*)?([^\→]+?)\s*→\s*Link\s*$'
                match = re.search(project_link_pattern, original_line)
                
                if match:
                    # Save previous project if exists
                    if current_project:
                        project_descriptions[current_project] = current_description
                        found_projects.append(current_project)

                    # Extract project title (group 1) and preserve original casing
                    project_title = match.group(1).strip()
                    if len(project_title) > 3:
                        current_project = project_title
                        current_description = []
                    else:
                        current_project = None
                elif current_project:
                    # This is a description line for the current project
                    if line.startswith('•') or line.startswith('-'):
                        desc_text = line[1:].strip() if len(line) > 1 else line
                        if desc_text:  # Only add non-empty descriptions
                            current_description.append(desc_text)
                    elif line and not any(header in line.lower() for header in end_section_headers):
                        # Additional description line
                        current_description.append(original_line.strip())
                elif len(line) > 5 and not any(keyword in line.lower() for keyword in ['technologies:', 'developed', 'built']):
                    # Heuristic: standalone line might be a project title without link
                    if current_project:
                        project_descriptions[current_project] = current_description
                        found_projects.append(current_project)
                    current_project = original_line.strip()
                    current_description = []

                i += 1

            # Save the last project
            if current_project:
                project_descriptions[current_project] = current_description
                found_projects.append(current_project)

            entities["projects"] = found_projects
            entities["project_descriptions"] = project_descriptions
            return entities
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {}
    
    def process_resume(self, pdf_path: str, resume_id: str = None) -> Dict:
        """Process resume: extract text, chunk, embed, and store"""
        if not resume_id:
            resume_id = f"UPLOADED_{hash(pdf_path) % 10000:04d}"
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Chunk text
        chunks = self.recursive_chunking(text)
        
        # Generate embeddings and store
        new_chunks_data = []
        for i, chunk in enumerate(chunks):
            embedding = encoder.encode(chunk)
            
            chunk_data = {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_chunk_{i}",
                "chunk_text": chunk,
                "embedding": embedding,
                "metadata": {
                    "source": "uploaded_resume",
                    "entities": entities,
                    "filename": os.path.basename(pdf_path)
                }
            }
            new_chunks_data.append(chunk_data)
        
        # Add to vectorstore
        if self.index:
            new_embeddings = np.array([item['embedding'] for item in new_chunks_data]).astype('float32')
            self.index.add(new_embeddings)
            self.chunks_data.extend(new_chunks_data)
            
            # Save updated vectorstore
            faiss.write_index(self.index, os.path.join(self.vectorstore_dir, "resume_index.faiss"))
            with open(os.path.join(self.vectorstore_dir, "chunks_data.pkl"), 'wb') as f:
                pickle.dump(self.chunks_data, f)
        
        return {
            "resume_id": resume_id,
            "text": text,
            "chunks": chunks,
            "entities": entities,
            "chunk_count": len(chunks)
        }
    
    def similarity_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar chunks in vectorstore"""
        if not self.index or len(self.chunks_data) == 0:
            return []
        
        # Encode query
        query_embedding = encoder.encode(query).astype('float32').reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks_data):
                results.append({
                    "chunk_data": self.chunks_data[idx],
                    "similarity_score": 1 - (distances[0][i] / 2),  # Convert distance to similarity
                    "distance": distances[0][i]
                })
        
        return results
    
    def analyze_resume_job_match(self, resume_text: str, job_description: str) -> Dict:
        """Analyze resume match with job description"""
        # Extract key components from job description
        required_skills = self.extract_required_skills(job_description)
        required_experience = self.extract_experience_requirements(job_description)
        required_education = self.extract_education_requirements(job_description)
        
        # Extract from resume
        resume_entities = self.extract_entities(resume_text)
        resume_skills = resume_entities.get("skills", [])
        resume_experience_years = self.extract_experience_from_resume(resume_text)
        resume_education = self.extract_education_from_resume(resume_text)
        
        # Calculate match scores
        skills_match = self.calculate_skills_match(resume_skills, required_skills)
        experience_match = self.calculate_experience_match(resume_experience_years, required_experience)
        education_match = self.calculate_education_match(resume_education, required_education)
        
        # Overall score (weighted average)
        overall_score = (skills_match * 0.6 + experience_match * 0.2 + education_match * 0.2)
        
        return {
            "overall_match_percentage": round(overall_score * 100, 2),
            "skills_match": {
                "percentage": round(skills_match * 100, 2),
                "required_skills": required_skills,
                "matched_skills": [skill for skill in required_skills if self.skill_match(skill, resume_skills)],
                "missing_skills": [skill for skill in required_skills if not self.skill_match(skill, resume_skills)]
            },
            "experience_match": {
                "percentage": round(experience_match * 100, 2),
                "required_experience": required_experience,
                "resume_experience": resume_experience_years
            },
            "education_match": {
                "percentage": round(education_match * 100, 2),
                "required_education": required_education,
                "resume_education": resume_education
            },
            "improvement_suggestions": self.generate_improvement_suggestions(
                resume_skills, required_skills, resume_experience_years, 
                required_experience, resume_education, required_education
            )
        }
    
    def extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description"""
        # Common skill indicators
        patterns = [
            r'(?:skills?:?\s*)(.*?)(?:\n|$)',
            r'(?:requirements?:?\s*)(.*?)(?:\n|$)',
            r'(?:qualifications?:?\s*)(.*?)(?:\n|$)',
            r'(?:must have:?)(.*?)(?:\n|$)',
            r'(?:required:?)(.*?)(?:\n|$)'
        ]
        
        skills = []
        job_lower = job_description.lower()
        
        # Look for programming languages and technologies
        tech_skills = [
            "python", "java", "javascript", "react", "angular", "vue", "node.js", 
            "express", "django", "flask", "spring", "c++", "c#", "ruby", "php",
            "sql", "mongodb", "postgresql", "mysql", "redis", "aws", "azure", 
            "google cloud", "docker", "kubernetes", "jenkins", "git", "github",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib",
            "tableau", "power bi", "excel", "agile", "scrum", "jira", "confluence"
        ]
        
        for skill in tech_skills:
            if skill in job_lower:
                skills.append(skill.title())
        
        # If no skills found with simple matching, use NER
        if len(skills) == 0 and self.ner_pipeline:
            entities = self.extract_entities(job_description)
            skills = entities.get("skills", [])
        
        return list(set(skills))
    
    def extract_experience_requirements(self, job_description: str) -> int:
        """Extract required years of experience"""
        patterns = [
            r'(\d+)\s*\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s+of\s+(\d+)\s*\+?\s*years?',
            r'(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:working\s+)?experience',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                return int(matches[0])
        
        # Default values based on job level
        job_lower = job_description.lower()
        if any(term in job_lower for term in ["senior", "lead", "principal", "manager"]):
            return 5
        elif any(term in job_lower for term in ["junior", "associate", "entry"]):
            return 0
        else:
            return 2  # Default for mid-level
    
    def extract_education_requirements(self, job_description: str) -> str:
        """Extract required education level"""
        job_lower = job_description.lower()
        
        if any(term in job_lower for term in ["phd", "doctorate"]):
            return "PhD"
        elif any(term in job_lower for term in ["master", "ms", "m.s.", "mba"]):
            return "Master's"
        elif any(term in job_lower for term in ["bachelor", "bs", "b.s.", "ba", "b.a."]):
            return "Bachelor's"
        else:
            return "Bachelor's"  # Default assumption
    

    def extract_experience_from_resume(self, resume_text: str) -> int:
        """Extract years of experience from resume — only if explicitly mentioned or from work history"""
        try:
            # First, look for explicit "X years of experience" statements
            explicit_patterns = [
                r'(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience',
                r'experience\s+of\s+(\d+)\s*\+?\s*years?',
                r'(\d+)\s*\+?\s*years?\s+(?:of\s+)?(?:working\s+)?experience',
            ]
            
            for pattern in explicit_patterns:
                matches = re.findall(pattern, resume_text, re.IGNORECASE)
                if matches:
                    return int(matches[0])
            
            # Second, look at internships/jobs and try to calculate duration
            # This is more complex and error-prone, so we'll be conservative
            # Only count internships if they specify duration (e.g., "3-month internship")
            internship_patterns = [
                r'(\d+)\s*\-?\s*month\s+internship',
                r'internship\s+of\s+(\d+)\s+months?',
                r'(\d+)\s+months?\s+internship',
            ]
            
            total_months = 0
            for pattern in internship_patterns:
                matches = re.findall(pattern, resume_text, re.IGNORECASE)
                for match in matches:
                    total_months += int(match)
            
            # Convert to years (be conservative — only count full years)
            years_from_internships = total_months // 12
            
            # For students, internships are typically short — cap at 1 year max to avoid overestimation
            return min(years_from_internships, 1)
            
        except Exception as e:
            print(f"Error extracting experience: {e}")
            return 0  # Default to 0 if extraction fails
    
    def extract_education_from_resume(self, resume_text: str) -> str:
        """Extract education level by parsing the education section accurately"""
        try:
            # Normalize text
            text_lower = resume_text.lower()
            
            # Look for education section
            edu_section_start = -1
            edu_keywords = ["education", "academic background", "qualifications", "degrees"]
            
            for keyword in edu_keywords:
                idx = text_lower.find(keyword)
                if idx != -1:
                    edu_section_start = idx
                    break
            
            if edu_section_start == -1:
                # No education section found, fallback to keyword search (but be cautious)
                if any(term in text_lower for term in ["phd", "doctorate"]):
                    return "PhD"
                elif any(term in text_lower for term in ["master", "ms", "m.s.", "m.sc", "mba"]):
                    return "Master's"
                elif any(term in text_lower for term in ["bachelor", "bs", "b.s.", "b.sc", "ba", "b.a.", "btech", "b.tech"]):
                    return "Bachelor's"
                else:
                    return "Not specified"
            
            # Extract education section (until next major section or end)
            next_section_start = len(resume_text)
            section_headers = ["experience", "work", "projects", "skills", "certifications", "extracurricular", "achievements"]
            
            for header in section_headers:
                idx = text_lower.find(header, edu_section_start + 5)  # +5 to avoid matching the same "Education" header
                if idx != -1 and idx < next_section_start:
                    next_section_start = idx
            
            edu_section = resume_text[edu_section_start:next_section_start]
            
            # Now analyze the education section for degrees
            lines = edu_section.split('\n')
            degrees = []
            
            for line in lines:
                line_lower = line.lower()
                if any(term in line_lower for term in ["phd", "ph.d", "doctorate", "doctoral"]):
                    degrees.append("PhD")
                elif any(term in line_lower for term in ["master", "ms", "m.s.", "m.sc", "mba", "ma", "m.a.", "mtech", "m.tech"]):
                    degrees.append("Master's")
                elif any(term in line_lower for term in ["bachelor", "bs", "b.s.", "b.sc", "ba", "b.a.", "btech", "b.tech", "undergraduate"]):
                    degrees.append("Bachelor's")
            
            # Return the highest degree found
            degree_priority = {"PhD": 3, "Master's": 2, "Bachelor's": 1}
            highest_degree = "Not specified"
            highest_priority = 0
            
            for degree in degrees:
                priority = degree_priority.get(degree, 0)
                if priority > highest_priority:
                    highest_priority = priority
                    highest_degree = degree
            
            return highest_degree
            
        except Exception as e:
            print(f"Error extracting education: {e}")
            return "Not specified"
    
    def skill_match(self, required_skill: str, resume_skills: List[str]) -> bool:
        """Check if a required skill is matched in resume skills"""
        required_lower = required_skill.lower()
        
        for resume_skill in resume_skills:
            resume_lower = resume_skill.lower()
            if required_lower in resume_lower or resume_lower in required_lower:
                return True
        
        return False
    
    def calculate_skills_match(self, resume_skills: List[str], required_skills: List[str]) -> float:
        """Calculate skills match percentage"""
        if len(required_skills) == 0:
            return 1.0
        
        matched_count = sum(1 for skill in required_skills if self.skill_match(skill, resume_skills))
        return matched_count / len(required_skills)
    
    def calculate_experience_match(self, resume_experience: int, required_experience: int) -> float:
        """Calculate experience match percentage"""
        if required_experience == 0:
            return 1.0
        
        if resume_experience >= required_experience:
            return 1.0
        else:
            return resume_experience / required_experience
    
    def calculate_education_match(self, resume_education: str, required_education: str) -> float:
        """Calculate education match percentage"""
        education_levels = {"Not specified": 0, "Bachelor's": 1, "Master's": 2, "PhD": 3}
        
        resume_level = education_levels.get(resume_education, 0)
        required_level = education_levels.get(required_education, 1)  # Default to Bachelor's
        
        if resume_level >= required_level:
            return 1.0
        elif resume_level == required_level - 1:
            return 0.7
        elif resume_level == required_level - 2:
            return 0.3
        else:
            return 0.0
    
    def generate_improvement_suggestions(self, resume_skills: List[str], required_skills: List[str],
                                       resume_experience: int, required_experience: int,
                                       resume_education: str, required_education: str) -> List[str]:
        """Generate suggestions for improving resume"""
        suggestions = []
        
        # Skills suggestions
        missing_skills = [skill for skill in required_skills if not self.skill_match(skill, resume_skills)]
        if missing_skills:
            suggestions.append(f"Consider learning these skills: {', '.join(missing_skills[:5])}")
            suggestions.append("Add relevant projects or certifications to demonstrate these skills")
        
        # Experience suggestions
        experience_gap = required_experience - resume_experience
        if experience_gap > 0:
            suggestions.append(f"You need {experience_gap} more years of experience for this role")
            suggestions.append("Consider internships, freelance work, or personal projects to build experience")
        
        # Education suggestions
        education_levels = {"Not specified": 0, "Bachelor's": 1, "Master's": 2, "PhD": 3}
        resume_level = education_levels.get(resume_education, 0)
        required_level = education_levels.get(required_education, 1)
        
        if resume_level < required_level:
            degree_names = {1: "Bachelor's", 2: "Master's", 3: "PhD"}
            suggestions.append(f"Consider pursuing a {degree_names[required_level]} degree")
            if required_level == 2:
                suggestions.append("Alternatively, consider relevant certifications to compensate for education")
        
        # General suggestions
        if len(suggestions) == 0:
            suggestions.append("Your resume is well-matched to this job description!")
            suggestions.append("Focus on highlighting your achievements and quantifiable results")
        else:
            suggestions.append("Tailor your resume summary to better align with the job description")
            suggestions.append("Use keywords from the job description throughout your resume")
        
        return suggestions
    
    def chat_with_resume(self, resume_text: str, question: str, job_description: str = None) -> str:
        """Chatbot functionality to answer questions about the resume"""
        # For questions about improvement suggestions
        if "improve" in question.lower() or "suggestion" in question.lower() or "recommend" in question.lower():
            if job_description:
                analysis = self.analyze_resume_job_match(resume_text, job_description)
                suggestions = analysis["improvement_suggestions"]
                return "Here are some suggestions to improve your resume:\n" + "\n".join([f"• {s}" for s in suggestions])
            else:
                return "To provide improvement suggestions, please provide a job description to compare against."
        
        # For skills recommendations
        # For questions about skills
        elif "skill" in question.lower() or "skills" in question.lower() or "proficient" in question.lower() or "knowledge" in question.lower():
            entities = self.extract_entities(resume_text)
            resume_skills = entities.get("skills", [])
            
            if resume_skills:
                response = "Based on your resume, here are your key skills:\n\n"
                for i, skill in enumerate(resume_skills, 1):
                    response += f"{i}. {skill}\n"
                
                # Add context about skill categories if available
                if any("python" in s.lower() for s in resume_skills):
                    response += "\n💡 You have strong programming skills in Python and related libraries."
                if any("react" in s.lower() for s in resume_skills):
                    response += "\n💡 You have experience with modern frontend frameworks like React.js."
                if any("aws" in s.lower() for s in resume_skills):
                    response += "\n💡 You have cloud computing experience with AWS."
                if any("machine learning" in s.lower() for s in resume_skills):
                    response += "\n💡 You have knowledge in Machine Learning and related tools."
            else:
                response = "I couldn't identify specific skills from your resume. Consider adding a clear 'Skills' section with relevant technologies and tools."
            
            return response
        
        # For project recommendations
        elif "project" in question.lower() or "build" in question.lower() or "develop" in question.lower():
            entities = self.extract_entities(resume_text)
            resume_projects = entities.get("projects", [])
            project_descriptions = entities.get("project_descriptions", {})
            resume_skills = entities.get("skills", [])
            
            if resume_projects:
                response = "Based on your resume, you've worked on these projects:\n\n"
                
                for project in resume_projects:
                    # Display project title in original casing
                    response += f"**{project}**\n"
                    descriptions = project_descriptions.get(project, [])
                    if descriptions:
                        for desc in descriptions:
                            if desc.strip():  # Only add non-empty descriptions
                                response += f"  • {desc}\n"
                    else:
                        response += "  • No description available\n"
                    response += "\n"
                
                # Add suggestions based on skills
                if "machine learning" in [s.lower() for s in resume_skills] or "pytorch" in [s.lower() for s in resume_skills]:
                    response += "\nConsider building an advanced ML project like a recommendation system or NLP application."
                elif "react" in [s.lower() for s in resume_skills] or "node.js" in [s.lower() for s in resume_skills]:
                    response += "\nConsider building a full-stack SaaS application with user authentication and payment integration."
                else:
                    response += "\nConsider expanding your project portfolio with something that showcases your strongest skills."
            else:
                response = "Consider building projects that demonstrate skills relevant to your target job. For example: a web application, data analysis project, or automation tool."
            
            return response
        
        # For certification recommendations
        elif "certification" in question.lower() or "certify" in question.lower() or "certificate" in question.lower():
            entities = self.extract_entities(resume_text)
            resume_skills = entities.get("skills", [])
            
            cert_suggestions = []
            if any("aws" in s.lower() for s in resume_skills):
                cert_suggestions.append("AWS Certified Solutions Architect")
            if any("azure" in s.lower() for s in resume_skills):
                cert_suggestions.append("Microsoft Azure Fundamentals")
            if any("google cloud" in s.lower() for s in resume_skills):
                cert_suggestions.append("Google Cloud Professional Cloud Architect")
            if any("python" in s.lower() for s in resume_skills):
                cert_suggestions.append("PCAP - Certified Associate in Python Programming")
            if any("data" in s.lower() or "analyst" in s.lower() for s in resume_skills):
                cert_suggestions.append("Google Data Analytics Professional Certificate")
            
            if cert_suggestions:
                return "Here are some certification recommendations based on your skills:\n" + "\n".join([f"• {c}" for c in cert_suggestions])
            else:
                return "Consider certifications relevant to your field, such as cloud certifications (AWS, Azure, GCP), programming language certifications, or industry-specific credentials."
        
        # For general questions about the resume
        else:
            # Use similarity search to find relevant chunks
            results = self.similarity_search(question, top_k=3)
            if results:
                # Combine the most relevant chunks
                context = "\n".join([result["chunk_data"]["chunk_text"] for result in results])
                
                # Simple response generation based on context
                if "experience" in question.lower():
                    years = self.extract_experience_from_resume(resume_text)
                    return f"Based on your resume, you have approximately {years} years of experience."
                
                elif "education" in question.lower():
                    education = self.extract_education_from_resume(resume_text)
                    return f"Your highest education level appears to be: {education}."
                
                elif "skill" in question.lower():
                    entities = self.extract_entities(resume_text)
                    skills = entities.get("skills", [])
                    if skills:
                        return f"Your resume shows skills in: {', '.join(skills[:10])}."
                    else:
                        return "I couldn't identify specific skills from your resume."
                
                else:
                    # Generic response with context
                    return f"Based on your resume: {context[:500]}..." if len(context) > 500 else f"Based on your resume: {context}"
            
            else:
                return "I couldn't find specific information in your resume to answer that question. Could you be more specific?"

# Initialize global analyzer
analyzer = ResumeAnalyzer()

# Sample job descriptions for demo
SAMPLE_JOB_DESCRIPTIONS = {
    "Software Engineer": """
    Job Title: Software Engineer
    Location: Remote
    Experience: 3+ years
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 3+ years of software development experience
    - Proficiency in Python, Java, or JavaScript
    - Experience with REST APIs and SQL databases
    - Familiarity with Git and Agile methodologies
    - Experience with cloud platforms (AWS, Azure, or GCP)
    
    Preferred Qualifications:
    - Master's degree in Computer Science
    - Experience with Docker and Kubernetes
    - Knowledge of React or Angular
    - Experience with CI/CD pipelines
    """,
    
    "Data Scientist": """
    Job Title: Data Scientist
    Location: New York, NY
    Experience: 2+ years
    
    Requirements:
    - Master's degree in Statistics, Mathematics, Computer Science, or related field
    - 2+ years of experience in data analysis and machine learning
    - Proficiency in Python and SQL
    - Experience with pandas, numpy, scikit-learn
    - Strong statistical and mathematical skills
    - Experience with data visualization tools (Tableau, Power BI, or matplotlib)
    
    Preferred Qualifications:
    - PhD in a quantitative field
    - Experience with TensorFlow or PyTorch
    - Experience with big data technologies (Spark, Hadoop)
    - Experience with cloud platforms (AWS SageMaker, Google AI Platform)
    """,
    
    "Product Manager": """
    Job Title: Product Manager
    Location: San Francisco, CA
    Experience: 5+ years
    
    Requirements:
    - Bachelor's degree in Business, Computer Science, or related field
    - 5+ years of product management experience
    - Strong understanding of Agile methodologies
    - Excellent communication and leadership skills
    - Experience with product analytics tools
    - Ability to create product roadmaps and prioritize features
    
    Preferred Qualifications:
    - MBA or Master's degree
    - Technical background with ability to understand engineering concepts
    - Experience in SaaS or B2B products
    - Experience with Jira, Confluence, and other collaboration tools
    """,
    
    "DevOps Engineer": """
    Job Title: DevOps Engineer
    Location: Remote
    Experience: 4+ years
    
    Requirements:
    - Bachelor's degree in Computer Science or related field
    - 4+ years of experience in DevOps or SRE roles
    - Proficiency with Linux/Unix systems
    - Experience with AWS, Azure, or GCP
    - Experience with Docker, Kubernetes, and containerization
    - Experience with CI/CD tools (Jenkins, GitLab CI, CircleCI)
    - Experience with infrastructure as code (Terraform, CloudFormation)
    - Strong scripting skills (Python, Bash, or similar)
    
    Preferred Qualifications:
    - AWS Certified DevOps Engineer certification
    - Experience with monitoring tools (Prometheus, Grafana, Datadog)
    - Experience with configuration management (Ansible, Chef, Puppet)
    """,
    
    "UX Designer": """
    Job Title: UX Designer
    Location: Remote
    Experience: 3+ years
    
    Requirements:
    - Bachelor's degree in Design, HCI, or related field
    - 3+ years of UX design experience
    - Proficiency with design tools (Figma, Sketch, Adobe XD)
    - Strong portfolio showcasing UX design process
    - Experience with user research and usability testing
    - Understanding of responsive design and accessibility standards
    - Ability to create wireframes, prototypes, and high-fidelity designs
    
    Preferred Qualifications:
    - Master's degree in Design or HCI
    - Experience with front-end development (HTML, CSS, JavaScript)
    - Experience with design systems
    - Experience in Agile environments
    """
}