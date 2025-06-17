from openai import OpenAI


if __name__ == '__main__':
    client = OpenAI()
    output_path = "llm_results/results.jsonl"

    file_response = client.files.content("file-CYcZfckDSi2bMrdqxLayqb")
    print(file_response.text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(file_response.text)
    print(f"✅ Batch output written to {output_path}")