import os
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from openai import OpenAI

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context. 
The context may contain anonymized information, which is represented by placeholder tags. 
When you encounter a placeholder tag, please respond with the tag itself instead of trying to guess the original information. 
Example: 
User: My name is <PERSON> and my phone number is <PHONE_NUMBER>.
Assistant: Hello <PERSON>, how can I assist you today? I see that your phone number is <PHONE_NUMBER>."""

text = "My name is John Smith and my phone number is 555-2368"

# Custom recognizer for 7-digit phone numbers (e.g. 555-2368, 5552368)
short_phone_pattern = Pattern(
    name="short_phone",
    regex=r"\b\d{3}[-.\s]?\d{4}\b",
    score=0.7,
)
short_phone_recognizer = PatternRecognizer(
    supported_entity="PHONE_NUMBER",
    patterns=[short_phone_pattern],
)

# Set up Presidio engines
analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(short_phone_recognizer)
anonymizer = AnonymizerEngine()

# Detect PII entities (name + phone number)
results = analyzer.analyze(
    text=text,
    entities=["PERSON", "PHONE_NUMBER"],
    language="en",
)

# Anonymize with placeholder tags so we can reverse it later
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
anonymized_text = anonymized.text

print("Original text:", text)
print("Anonymized text:", anonymized_text)

# Build a mapping from placeholder -> original value for de-anonymization
# anonymized.items have positions in the anonymized text;
# analyzer results have positions in the original text.
# Sort both by position and pair them to get the correct mapping.
sorted_anon_items = sorted(anonymized.items, key=lambda x: x.start)
sorted_results = sorted(results, key=lambda x: x.start)

placeholder_to_original = {}
for anon_item, result in zip(sorted_anon_items, sorted_results):
    placeholder = anonymized_text[anon_item.start:anon_item.end]
    original = text[result.start:result.end]
    placeholder_to_original[placeholder] = original

# Send anonymized text to OpenAI
client = OpenAI()  # uses OPENAI_API_KEY env var

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": anonymized_text},
    ],
)

anonymized_response = response.choices[0].message.content
print("Anonymized response:", anonymized_response)

# De-anonymize: replace placeholders back with original values
deanonymized_response = anonymized_response
for placeholder, original in placeholder_to_original.items():
    deanonymized_response = deanonymized_response.replace(placeholder, original)

print("De-anonymized response:", deanonymized_response)
