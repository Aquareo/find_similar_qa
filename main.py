import pandas as pd
from sentence_transformers import SentenceTransformer, util
from pathlib import Path


# Example usage
current_dir = Path(__file__).parent

query = "法国"  # Replace with your query
model_path = str(current_dir / "model"/"shibing624_text2vec_base_chinese" ) # Replace with your file path
file_path = str(current_dir / "qa_chinese_optimized.xlsx")  # Replace with your file path

# Step 2: Load sentence transformer model
model = SentenceTransformer("shibing624/text2vec-base-chinese")
def find_similar_qa(query, file_path, top_n=3):
    # Step 1: Read XLSX file
    try:
        df = pd.read_excel(file_path)
        if 'Question' not in df.columns or 'Answer' not in df.columns:
            raise ValueError("XLSX must contain 'Question' and 'Answer' columns")
    except Exception as e:
        return f"Error reading XLSX: {str(e)}"

    questions = df['Question'].tolist()
    answers = df['Answer'].tolist()



    # Step 3: Encode query and questions
    query_embedding = model.encode(query, convert_to_tensor=True)
    question_embeddings = model.encode(questions, convert_to_tensor=True)

    # Step 4: Compute cosine similarities
    similarities = util.cos_sim(query_embedding, question_embeddings)[0]

    # Step 5: Get top N indices and scores
    top_indices = similarities.argsort(descending=True)[:top_n]
    results = [
        {
            'Question': questions[idx],
            'Answer': answers[idx],
            'Similarity': similarities[idx].item()
        }
        for idx in top_indices
    ]

    # Debug: Print results to verify structure
    print("Debug: Results structure:", results)
    return results


top_matches = find_similar_qa(query, file_path, top_n=5)

# Print results with error handling
if isinstance(top_matches, str):
    print(top_matches)  # Handle error message from function
else:
    for i, match in enumerate(top_matches, 1):
        # Debug: Print match type and content
        print(f"Debug: Match {i} type: {type(match)}, content: {match}")
        if isinstance(match, dict):
            print(f"Match {i}:")
            print(f"Question: {match['Question']}")
            print(f"Answer: {match['Answer']}")
            print(f"Similarity: {match['Similarity']:.4f}\n")
        else:
            print(f"Error: Match {i} is not a dictionary, got {type(match)}: {match}")
