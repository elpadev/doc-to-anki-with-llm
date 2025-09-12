
# doc-to-anki-with-llm

Generate Anki decks from PDF documents using LLM-generated questions and answers.

## Overview

`doc-to-anki-with-llm` is a command-line tool that leverages large language models (LLMs) to automatically generate question-answer flashcards from PDF documents and export them as Anki decks (`.apkg`). This is ideal for students, educators, and self-learners who want to quickly create high-quality study materials from textbooks, lecture notes, or any PDF resource.

## Features

- **Automatic Q&A Generation:** Uses an LLM to generate questions and answers from document content.
- **PDF Support:** Processes each page of a PDF as a separate context for flashcard generation.
- **Customizable Decks:** Set the deck name and output file.
- **Page Range Selection:** Choose which pages of the PDF to process.
- **OpenAI API Integration:** Uses OpenAI models (e.g., GPT-4o-mini) for Q&A generation.

## Installation

1. **Clone the repository:**
	```bash
	git clone https://github.com/elpadev/doc-to-anki-with-llm.git
	cd doc-to-anki-with-llm
	```

2. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```

3. **Set up your OpenAI API key:**
	- Create a `.env` file in the project root (optional) and add:
	  ```env
	  OPENAI_API_KEY=your_openai_api_key_here
	  ```
	- Or, you will be prompted for your API key at runtime.

## Usage

Run the script from the command line:

```bash
python src/main.py <pdf-file> [--deck-name DECK] [--output FILE] [--start-page N] [--end-page M]
```

### Arguments

- `<pdf-file>`: Path to the PDF file to process (required)
- `--deck-name`: Name of the Anki deck (default: `Country Capitals`)
- `--output`: Output Anki package file (default: `output.apkg`)
- `--start-page`: Start page number (1-based, inclusive)
- `--end-page`: End page number (1-based, inclusive)

### Example

Generate an Anki deck from pages 10 to 20 of `mybook.pdf`:

```bash
python src/main.py mybook.pdf --deck-name "My Book Deck" --output mybook.apkg --start-page 10 --end-page 20
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key. Can be set in a `.env` file or as an environment variable.

## How It Works

1. Loads the specified PDF and (optionally) selects a page range.
2. For each page, sends the content to the LLM with a prompt to generate Q&A pairs.
3. Structures the Q&A pairs as Anki notes and adds them to a deck.
4. Exports the deck as an `.apkg` file, ready to import into Anki.

## Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for bug fixes, new features, or improvements.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to your branch and open a pull request

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

- [genanki](https://github.com/kerrickstaley/genanki) for Anki deck generation
- [LangChain](https://github.com/langchain-ai/langchain) for LLM integration
- [OpenAI](https://openai.com/) for language models
