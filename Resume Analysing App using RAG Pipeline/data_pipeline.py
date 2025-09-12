import os
import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import re
import random
import zipfile

# Initialize sentence transformer for embeddings
encoder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', token=False)

class SyntheticDataPipeline:
    def __init__(self, data_dir="data/synthetic_resumes", vectorstore_dir="vectorstore"):
        self.data_dir = data_dir
        self.vectorstore_dir = vectorstore_dir
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(vectorstore_dir, exist_ok=True)
        
    def download_kaggle_data(self, dataset_name="prasoonkottarathil/btad"):
        """Download dataset from Kaggle"""
        try:
            api = KaggleApi()
            api.authenticate()
            api.dataset_download_files(dataset_name, path=self.data_dir, unzip=True)
            print(f"Dataset {dataset_name} downloaded successfully")
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            # Create synthetic data if Kaggle download fails
            self.create_synthetic_data()
    
    def create_synthetic_data(self, num_samples=1000):
        """Generate synthetic resume data"""
        job_titles = [
            "Software Engineer", "Data Scientist", "Product Manager", 
            "UX Designer", "DevOps Engineer", "Machine Learning Engineer",
            "Frontend Developer", "Backend Developer", "Full Stack Developer",
            "Data Analyst", "Business Analyst", "QA Engineer", "System Administrator"
        ]
        
        skills_list = [
            "Python", "Java", "JavaScript", "React", "Node.js", "SQL", "AWS", 
            "Docker", "Kubernetes", "TensorFlow", "PyTorch", "Pandas", "NumPy",
            "Git", "CI/CD", "Agile", "REST APIs", "GraphQL", "MongoDB", "PostgreSQL"
        ]
        
        education_levels = ["Bachelor's", "Master's", "PhD"]
        degrees = ["Computer Science", "Engineering", "Mathematics", "Physics", "Statistics"]
        
        synthetic_data = []
        
        for i in range(num_samples):
            resume_id = f"RES_{i:04d}"
            name = f"Candidate_{i}"
            job_title = random.choice(job_titles)
            
            # Generate random skills (3-8 skills per candidate)
            num_skills = random.randint(3, 8)
            skills = random.sample(skills_list, num_skills)
            
            # Generate education
            education_level = random.choice(education_levels)
            degree = random.choice(degrees)
            education = f"{education_level} in {degree}"
            
            # Generate experience (0-15 years)
            experience_years = random.randint(0, 15)
            
            # Generate projects (1-5 projects)
            num_projects = random.randint(1, 5)
            projects = [f"Project_{j}_{i}" for j in range(num_projects)]
            
            # Generate certifications (0-3)
            certifications = []
            if random.random() > 0.3:  # 70% chance of having certifications
                cert_count = random.randint(1, 3)
                certs = ["AWS Certified", "Google Cloud Certified", "Azure Certified", 
                        "PMP", "Scrum Master", "TensorFlow Developer"]
                certifications = random.sample(certs, min(cert_count, len(certs)))
            
            # Create resume text
            resume_text = f"""
            Name: {name}
            Target Position: {job_title}
            Summary: Experienced professional with {experience_years} years in the tech industry.
            Skills: {', '.join(skills)}
            Education: {education}
            Experience: {experience_years} years
            Projects: {', '.join(projects)}
            Certifications: {', '.join(certifications) if certifications else 'None'}
            """
            
            synthetic_data.append({
                "resume_id": resume_id,
                "name": name,
                "job_title": job_title,
                "skills": skills,
                "education": education,
                "experience_years": experience_years,
                "projects": projects,
                "certifications": certifications,
                "resume_text": resume_text.strip()
            })
        
        # Save to CSV
        df = pd.DataFrame(synthetic_data)
        df.to_csv(os.path.join(self.data_dir, "synthetic_resumes.csv"), index=False)
        print(f"Generated {num_samples} synthetic resumes")
        return df
    
    def recursive_chunking(self, text, max_chunk_size=500, overlap=50):
        """Recursively chunk text with overlap"""
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chunk_size
            
            # Don't go beyond text length
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to find a natural break (sentence end or newline)
            cut_point = end
            for i in range(end, start, -1):
                if text[i-1:i+1] in ['. ', '! ', '? ', '\n', '\r\n']:
                    cut_point = i + 1
                    break
            
            chunk = text[start:cut_point]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = cut_point - overlap
            if start < 0:
                start = 0
        
        return chunks
    
    def process_resumes(self, df):
        """Process resumes: chunking and embedding"""
        chunks_data = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing resumes"):
            resume_text = row['resume_text']
            chunks = self.recursive_chunking(resume_text)
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = encoder.encode(chunk)
                
                chunks_data.append({
                    "resume_id": row['resume_id'],
                    "chunk_id": f"{row['resume_id']}_chunk_{i}",
                    "chunk_text": chunk,
                    "embedding": embedding,
                    "metadata": {
                        "name": row['name'],
                        "job_title": row['job_title'],
                        "skills": row['skills'],
                        "experience_years": row['experience_years']
                    }
                })
        
        return chunks_data
    
    def create_vectorstore(self, chunks_data):
        """Create and save FAISS vectorstore"""
        # Extract embeddings and create index
        embeddings = np.array([item['embedding'] for item in chunks_data]).astype('float32')
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Save index
        faiss.write_index(index, os.path.join(self.vectorstore_dir, "resume_index.faiss"))
        
        # Save chunks data
        with open(os.path.join(self.vectorstore_dir, "chunks_data.pkl"), 'wb') as f:
            pickle.dump(chunks_data, f)
        
        print(f"Created vectorstore with {len(chunks_data)} chunks")
        return index, chunks_data
    
    def run_pipeline(self):
        """Run the complete data pipeline"""
        print("Starting data pipeline...")
        
        # Try to download from Kaggle, fallback to synthetic data
        try:
            
            # Load and process the downloaded data
            # For simplicity, we'll use our synthetic data approach
            df = self.create_synthetic_data()
        except Exception as e:
            print(f"Using synthetic data due to error: {e}")
            df = self.create_synthetic_data()
        
        # Process resumes
        chunks_data = self.process_resumes(df)
        
        # Create vectorstore
        index, chunks_data = self.create_vectorstore(chunks_data)
        
        print("Data pipeline completed successfully!")
        return index, chunks_data

# Run the pipeline if this file is executed directly
if __name__ == "__main__":
    pipeline = SyntheticDataPipeline()
    pipeline.run_pipeline()