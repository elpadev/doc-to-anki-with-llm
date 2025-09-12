#!/usr/bin/env python3
"""
Main script to generate Anki decks from documents using LLMs.
"""

import argparse
import asyncio
import getpass
import logging
import os
import random
import sys
from typing import List

import dotenv
import genanki
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

import prompt

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def get_openai_api_key() -> str:
    """Prompt for OpenAI API key if not set in environment."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = getpass.getpass("Enter API key for OpenAI: ")
        os.environ["OPENAI_API_KEY"] = api_key
    return api_key


def create_anki_model(model_id: int) -> genanki.Model:
    """Create a simple Anki model."""
    return genanki.Model(
        model_id,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ]
    )


def create_anki_deck(deck_id: int, deck_name: str) -> genanki.Deck:
    """Create an Anki deck."""
    return genanki.Deck(deck_id, deck_name)


async def load_pdf_pages(file_path: str) -> List:
    """Asynchronously load pages from a PDF file."""
    loader = PyPDFLoader(file_path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page)
    return pages


class QuestionAndAnswerFormat(BaseModel):
    """Structure for a single flashcard."""
    question: str = Field(description="The question for the flashcard")
    answer: str = Field(
        description="The answer to the question for the flashcard")


class QuestionAndAnswerListFormat(BaseModel):
    """Structure for a list of flashcards."""
    qa_list: List[QuestionAndAnswerFormat] = Field(
        description="A list of question and answer pairs")


def validate_pdf_path(pdf_path: str) -> None:
    """Validate that the PDF file exists and is a file."""
    if not os.path.isfile(pdf_path):
        logging.error(
            "PDF file '%s' does not exist or is not a file.", pdf_path)
        sys.exit(1)


def add_notes_from_pages(pages, chat_model, my_model, my_deck) -> int:
    """Process pages, generate Q&A, and add notes to the deck. Returns number of notes added."""
    note_count = 0
    for page in pages:
        messages = [
            SystemMessage(content=prompt.prompt),
            HumanMessage(content=page.page_content)
        ]
        try:
            resp = chat_model.invoke(messages)
        except Exception as e:
            logging.warning("LLM invocation failed for a page: %s", e)
            continue
        for qa in resp.qa_list:
            logging.info("Q: %s\nA: %s", qa.question, qa.answer)
            try:
                my_note = genanki.Note(
                    model=my_model,
                    fields=[qa.question, qa.answer]
                )
                my_deck.add_note(my_note)
                note_count += 1
            except Exception as e:
                logging.warning("Failed to add note: %s", e)
    return note_count


def main():
    parser = argparse.ArgumentParser(
        description="Generate Anki deck from PDF using LLM.")
    parser.add_argument('pdf', help='Path to the PDF file to process')
    parser.add_argument(
        '--deck-name', default='Country Capitals', help='Name of the Anki deck')
    parser.add_argument('--output', default='output.apkg',
                        help='Output Anki package file')
    parser.add_argument('--start-page', type=int, default=None,
                        help='Start page number (1-based, inclusive)')
    parser.add_argument('--end-page', type=int, default=None,
                        help='End page number (1-based, inclusive)')
    args = parser.parse_args()

    validate_pdf_path(args.pdf)
    get_openai_api_key()
    chat_model = init_chat_model(
        "gpt-5-mini", model_provider="openai").with_structured_output(QuestionAndAnswerListFormat)

    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)
    my_model = create_anki_model(model_id)
    my_deck = create_anki_deck(deck_id, args.deck_name)

    # Load PDF pages (async)
    try:
        pages = asyncio.run(load_pdf_pages(args.pdf))
    except Exception as e:
        logging.error("Error loading PDF: %s", e)
        sys.exit(1)

    # Select page range if specified
    total_pages = len(pages)
    start_idx = 0
    end_idx = total_pages
    if args.start_page is not None:
        if args.start_page < 1 or args.start_page > total_pages:
            logging.error(
                "Start page %d is out of range (1-%d)", args.start_page, total_pages)
            sys.exit(1)
        start_idx = args.start_page - 1
    if args.end_page is not None:
        if args.end_page < 1 or args.end_page > total_pages:
            logging.error(
                "End page %d is out of range (1-%d)", args.end_page, total_pages)
            sys.exit(1)
        end_idx = args.end_page
    if start_idx >= end_idx:
        logging.error("Start page must be less than or equal to end page.")
        sys.exit(1)
    selected_pages = pages[start_idx:end_idx]

    note_count = add_notes_from_pages(
        selected_pages, chat_model, my_model, my_deck)

    if note_count == 0:
        logging.warning("No notes were added to the deck.")
    else:
        genanki.Package(my_deck).write_to_file(args.output)
        logging.info(
            "Anki deck written to %s with %d notes.", args.output, note_count)


if __name__ == '__main__':
    main()
