from openai import OpenAI

if __name__ == '__main__':
    client = OpenAI()

    batch_input_file = client.files.create(
        file=open("openai_batch_input.jsonl", "rb"),
        purpose="batch"
    )

    print(batch_input_file)

    batch_input_file_id = batch_input_file.id
    client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "classification of pizza ontology"
        }
    )
