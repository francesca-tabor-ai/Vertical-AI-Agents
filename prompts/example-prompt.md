# Example Prompt Template

## Use Case
Document classification

## Variables
- `{document_text}` - The document content to classify
- `{categories}` - List of valid categories

## Prompt

```
You are a document classifier. Analyze the following document and classify it into one of the provided categories.

Categories: {categories}

Document:
{document_text}

Respond with only the category name.
```

## Expected Output
Single category name from the provided list.

## Notes
- Keep documents under 100k tokens for optimal performance
- Use Claude Haiku for high-volume classification tasks
