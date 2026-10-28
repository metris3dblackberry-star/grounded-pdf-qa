from app.pdf_parse import boilerplate_lines, clean_page, pack_chunks, split_sentences


def test_boilerplate_detects_repeated_footer_with_changing_page_numbers():
    topics = ["wages", "tips", "deposits", "penalties", "forms", "credits", "records", "benefits", "travel", "meals"]
    pages = [[f"This page explains {t}.", f"Page {i}", "Publication 15 (2026)"] for i, t in enumerate(topics, 1)]
    bp = boilerplate_lines(pages)
    assert "publication # (#)" in bp
    assert "page #" in bp
    assert clean_page(pages[3], bp) == "This page explains penalties."


def test_clean_page_joins_hyphenated_words_and_lines():
    text = clean_page(["The employ-", "ment tax is due", "• quarterly."], set())
    assert text == "The employment tax is due - quarterly."


def test_split_sentences():
    assert split_sentences("First one. Second one? Third (here).") == ["First one.", "Second one?", "Third (here)."]


def test_pack_chunks_respects_size_and_overlap():
    text = " ".join(f"Sentence number {i} has exactly seven words." for i in range(60))
    chunks = pack_chunks(text, max_words=70, overlap=14)
    assert len(chunks) > 3
    assert all(len(c.split()) <= 70 + 14 for c in chunks)
    # consecutive chunks share the overlap
    assert chunks[0].split()[-14:] == chunks[1].split()[:14]


def test_pack_chunks_merges_short_tail_into_previous_chunk():
    text = " ".join(["word"] * 69) + ". Tail here."
    chunks = pack_chunks(text, max_words=70, overlap=10)
    assert len(chunks) == 1
    assert chunks[0].endswith("Tail here.")


def test_pack_chunks_hard_splits_overlong_sentence():
    text = " ".join(f"w{i}" for i in range(250)) + "."
    chunks = pack_chunks(text, max_words=100, overlap=20)
    assert all(len(c.split()) <= 100 for c in chunks)
    assert chunks[0].split()[-20:] == chunks[1].split()[:20]
