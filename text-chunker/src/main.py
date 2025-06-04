import asyncio
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from typing import List, Any
from openai import OpenAI
from dotenv import load_dotenv
import json
import re
from pprint import pprint

# Load environment variables
load_dotenv()

app = FastAPI(title="Text Chunker", description="Split fiction text into singular scenes")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

DEFAULT_MODEL = "google/gemini-2.5-flash-preview-05-20"
# Configuration for large text processing
TARGET_CHUNK_SIZE_WORDS = 5000  # Target words for major chunks
WORD_COUNT_SLACK = 500      # How many words +/- to look for a natural break
MIN_CHUNK_SIZE_WORDS = 1000   # Minimum size for a chunk to be processed

class TextInput(BaseModel):
    text: str


class Scene(BaseModel):
    elementi_narrativi: str
    personaggi: str
    ambientazione: str
    mood_vibe: str
    azione_in_corso: str


class ScenesResponse(BaseModel):
    scenes: List[Scene]


async def _call_llm(
    current_client: OpenAI,
    prompt_content: str,
    system_message: str,
    model: str
) -> str:
    """Helper function to make an API call to the LLM."""
    response = await asyncio.to_thread( # Use asyncio.to_thread for blocking I/O
        current_client.chat.completions.create,
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_content},
        ]
    )
    content = response.choices[0].message.content
    if content is None:
        raise HTTPException(status_code=500, detail="LLM response content is empty.")
    return content


def _get_json_payload_from_llm_content(llm_content: str) -> str:
    """Extracts the JSON array string from the LLM's raw text output."""
    json_match = re.search(r"\[.*\]", llm_content, re.DOTALL)
    if json_match:
        return json_match.group(0)
    # Fallback: assume the entire content is the JSON payload if no specific array is found
    return llm_content


def _parse_and_validate_scenes(json_payload: str) -> List[Scene]:
    """
    Parses a JSON string and validates it into a list of Scene objects.
    Raises json.JSONDecodeError, ValueError, or pydantic.ValidationError on failure.
    """
    # Can raise json.JSONDecodeError if json_payload is not valid JSON
    scenes_data = json.loads(json_payload)

    # Raise ValueError if the top-level structure isn't a list
    if not isinstance(scenes_data, list):
        raise ValueError(f"Expected a JSON list/array, but got {type(scenes_data).__name__}. Payload preview: {json_payload[:200]}...")

    validated_scenes: List[Scene] = []
    try:
        # This can raise pydantic.ValidationError if items don't match Scene model,
        # or TypeError if an item in scenes_data is not a mapping (dict) for ** unpacking.
        for i, scene_item in enumerate(scenes_data):
            if not isinstance(scene_item, dict):
                raise ValueError(f"Item at index {i} in JSON array is not a dictionary (got {type(scene_item).__name__}). Payload preview: {json_payload[:200]}...")
            validated_scenes.append(Scene(**scene_item))
        return validated_scenes
    except TypeError as e:
        # Convert TypeError (e.g. from ** non-dict) to a ValueError for consistent handling
        raise ValueError(f"Error during scene model instantiation, possibly due to non-dict item: {str(e)}. Payload preview: {json_payload[:200]}...")
    # pydantic.ValidationError will propagate naturally if Scene(**scene_item) fails.


def _build_fixer_prompt(original_text: str, malformed_json_payload: str, validation_errors: Any) -> str:
    """Constructs the prompt for the fixer LLM call."""
    return f"""
Sei un assistente AI specializzato nella correzione di JSON malformati in base a uno schema Pydantic.
Il precedente tentativo di estrarre scene da un testo ha prodotto un JSON che non ha superato la validazione.

Testo originale analizzato:
{original_text}

JSON malformato ricevuto (o intero output se il JSON non è stato estratto correttamente):
{malformed_json_payload}

Errori di validazione Pydantic:
{validation_errors}

Il formato JSON corretto DEVE essere un array di oggetti. Ogni oggetto DEVE contenere ESATTAMENTE i seguenti campi come stringhe:
- `elementi_narrativi`
- `personaggi`
- `ambientazione`
- `mood_vibe`
- `azione_in_corso`

Per favore, correggi il JSON malformato per conformarlo rigorosamente a questo schema.
Restituisci SOLO l'array JSON corretto, senza testo aggiuntivo o spiegazioni.
Non inventare informazioni non presenti nel testo originale o nel JSON malformato; se necessario, ometti i campi che non possono essere popolati in modo affidabile, ma assicurati che i campi richiesti siano presenti, anche se con stringhe vuote se il contenuto non può essere derivato.
"""

async def split_text_into_scenes_logic(text: str) -> ScenesResponse:
    initial_prompt = f"""
Sei un esperto analista letterario e un narratore visivo. Il tuo compito è dividere il seguente testo di narrativa in scene individuali.
Per ogni scena, immagina di scattare un'istantanea da utilizzare per un servizio di generazione di immagini.

Pertanto, per ogni scena, fornisci:
Una scomposizione dettagliata delle componenti visive e narrative della scena con le seguenti chiavi:
    *   `elementi_narrativi`: (stringa) Elementi narrativi chiave presenti (ad esempio, oggetti significativi, simboli).
    *   `personaggi`: (stringa) Personaggi coinvolti, dettagliando il loro aspetto, espressioni ed eventuali interazioni se descritte.
    *   `ambientazione`: (stringa) L'ambientazione e l'ambiente (ad esempio, luogo, ora del giorno, tempo atmosferico, dettagli specifici dell'ambiente circostante).
    *   `mood_vibe`: (stringa) L'atmosfera o il mood generale della scena (ad esempio, teso, misterioso, calmo, gioioso). Se non esplicitamente chiaro, puoi dedurlo o indicare 'N/A'.
    *   `azione_in_corso`: (stringa) L'azione principale, l'evento o le pose dei personaggi che si svolgono nella scena.

Formatta la tua risposta come un array JSON. Ogni oggetto nell'array deve rappresentare una scena e contenere rigorosamente SOLO i seguenti campi: `elementi_narrativi`, `personaggi`, `ambientazione`, `mood_vibe`, e `azione_in_corso`.

Testo da analizzare:
{text}

Assicurati che le scene siano complete e non vengano interrotte a metà frase. Cerca interruzioni narrative naturali.
Concentrati sull'estrazione di dettagli visivi e descrittivi per ogni campo specificato.
NON includere il testo completo della scena nella tua risposta, ma solo i dati strutturati richiesti.
"""

    system_message_initial = "You are a literary analyst expert at identifying scene boundaries in fiction."

    llm_content_initial = ""
    json_payload_initial = ""

    try:
        print("--- Attempting Initial LLM Call ---")
        llm_content_initial = await _call_llm(client, initial_prompt, system_message_initial, DEFAULT_MODEL)
        print(f"Initial LLM raw output (first 1000 chars):\n{llm_content_initial[:1000]} ...\n")

        json_payload_initial = _get_json_payload_from_llm_content(llm_content_initial)
        print(f"Extracted JSON payload from initial call (first 1000 chars):\n{json_payload_initial[:1000]} ...\n")

        scenes = _parse_and_validate_scenes(json_payload_initial)
        print("--- Initial parsing and validation successful ---")
        return ScenesResponse(scenes=scenes)

    except (json.JSONDecodeError, ValidationError, ValueError) as e_initial:
        error_type_name = type(e_initial).__name__
        error_message_detail = e_initial.errors() if isinstance(e_initial, ValidationError) else str(e_initial)

        error_details_for_log = (
            f"Initial {error_type_name}: {error_message_detail}. "
            f"Original JSON payload tried (first 500 chars): {str(json_payload_initial)[:500]}..."
        )
        print(f"--- Error during initial processing: {error_details_for_log} ---")
        print("--- Attempting to fix with a second LLM call (Fixer Agent) ---")

        fixer_input_payload = json_payload_initial
        if not fixer_input_payload and llm_content_initial:
            print("(Using full initial LLM content for fixer as extracted payload was empty)")
            fixer_input_payload = llm_content_initial

        fixer_prompt = _build_fixer_prompt(text, fixer_input_payload, error_message_detail)
        system_message_fixer = "You are an AI assistant specialized in correcting malformed JSON based on a Pydantic schema."

        llm_content_fixer = "" # Initialize for broader scope in case of error before assignment
        json_payload_fixer = ""
        try:
            llm_content_fixer = await _call_llm(client, fixer_prompt, system_message_fixer, DEFAULT_MODEL)
            print(f"Fixer LLM raw output (first 1000 chars):\n{llm_content_fixer[:1000]} ...\n")

            json_payload_fixer = _get_json_payload_from_llm_content(llm_content_fixer)
            print(f"Extracted JSON payload from fixer call (first 1000 chars):\n{json_payload_fixer[:1000]} ...\n")

            fixed_scenes = _parse_and_validate_scenes(json_payload_fixer)
            print("--- Fixer parsing and validation successful ---")
            return ScenesResponse(scenes=fixed_scenes)

        except (json.JSONDecodeError, ValidationError, ValueError) as e_fixer:
            fixer_error_type_name = type(e_fixer).__name__
            fixer_error_message_detail = e_fixer.errors() if isinstance(e_fixer, ValidationError) else str(e_fixer)
            final_error_message = (
                f"Fixer attempt also failed. \nInitial error was: ({error_details_for_log}). \n"
                f"Fixer error ({fixer_error_type_name}): {fixer_error_message_detail}. \n"
                f"Fixer JSON payload tried (first 500 chars): {str(json_payload_fixer)[:500]}..."
            )
            print(f"--- Error during fixer processing: {final_error_message} ---")
            raise HTTPException(status_code=500, detail=final_error_message)
        except HTTPException as http_e_fixer: # from _call_llm in fixer
            err_msg = f"HTTPException during fixer LLM call: {http_e_fixer.detail}. Initial error: {error_details_for_log}"
            print(f"--- {err_msg} ---")
            raise HTTPException(status_code=500, detail=err_msg)
        except Exception as e_unhandled_fixer:
            unhandled_fixer_msg = f"Unexpected error during fixer stage: {str(e_unhandled_fixer)}. Initial error: {error_details_for_log}. Fixer raw output (first 500): {str(llm_content_fixer)[:500]}"
            print(f"--- {unhandled_fixer_msg} ---")
            raise HTTPException(status_code=500, detail=unhandled_fixer_msg)

    except HTTPException as http_e_initial: # from _call_llm in initial attempt
        err_msg = f"HTTPException during initial LLM call: {http_e_initial.detail}"
        print(f"--- {err_msg} ---")
        raise HTTPException(status_code=500, detail=err_msg) # Re-raise with potentially more context or just as is
    except Exception as e_unhandled_initial:
        unhandled_initial_msg = f"Unexpected error during initial stage: {str(e_unhandled_initial)}. Initial raw output (first 500): {str(llm_content_initial)[:500]}"
        print(f"--- {unhandled_initial_msg} ---")
        raise HTTPException(status_code=500, detail=unhandled_initial_msg)


def _find_natural_break_point(text_segment: str, start_offset: int, end_offset: int) -> int:
    """Tries to find a paragraph or sentence break within a range of the text_segment."""
    # Prioritize double newline (paragraph)
    # Search backwards from end_offset
    for i in range(end_offset, start_offset -1, -1):
        if text_segment[i-2:i] == "\n\n":
            return i
    # Then single newline (often sentence end or smaller break)
    for i in range(end_offset, start_offset - 1, -1):
        if text_segment[i-1:i] == "\n":
            return i
    # Then sentence-ending punctuation
    for i in range(end_offset, start_offset - 1, -1):
        if text_segment[i-1] in ('.', '?', '!'):
            return i
    return end_offset # Fallback to the hard end_offset if no better break found

def _create_non_overlapping_major_chunks(full_text: str, target_chunk_size_words: int, slack: int) -> List[str]:
    print(f"--- Starting to create non-overlapping major chunks. Target: {target_chunk_size_words} words, Slack: {slack} words ---")
    chunks: List[str] = []

    # Split by word boundaries for word counting, but operate on char offsets for slicing
    # A "word" here is roughly a non-whitespace sequence.
    word_tokens = re.findall(r'\S+\s*', full_text) # Tokenize into word + trailing space (or just word if at end)
    if not word_tokens:
        if full_text.strip(): # Handle case where text has no spaces but has content
             chunks.append(full_text)
             print(f"Created chunk 1 (no spaces in text): {len(re.findall(r'\\b\\w+\\b', full_text))} words, {len(full_text)} chars.")
             return chunks
        return []

    current_char_idx = 0
    processed_words_count = 0

    while current_char_idx < len(full_text):
        # Estimate end based on target_chunk_size_words from current_processed_words_count
        # This is an estimate to find a window for natural break point
        target_word_end_idx = min(processed_words_count + target_chunk_size_words, len(word_tokens))

        # Get char offset for this estimated word end
        estimated_char_end_offset = 0
        if target_word_end_idx > 0:
            # Sum lengths of word_tokens up to target_word_end_idx to get char position
            # This requires iterating part of word_tokens, but only over the current chunk's estimated length
            temp_char_len_for_estimate = current_char_idx # Start from current char_idx
            # Calculate the char length from processed_words_count up to target_word_end_idx
            # More directly: sum lengths of word_tokens from processed_words_count to target_word_end_idx
            # then add to current_char_idx
            estimated_additional_chars = sum(len(wt) for wt in word_tokens[processed_words_count:target_word_end_idx])
            estimated_char_end_offset = current_char_idx + estimated_additional_chars
        else:
             estimated_char_end_offset = current_char_idx

        # If it's the last potential chunk, try to take everything remaining
        # Check if remaining words are less than a chunk plus slack (meaning we should probably take all of it)
        if (len(word_tokens) - processed_words_count) < (target_chunk_size_words + slack):
            estimated_char_end_offset = len(full_text)

        # Define search range for a natural break
        slack_chars_approx = slack * 6 # Average word length 5 + 1 space
        search_start_char = max(current_char_idx, estimated_char_end_offset - slack_chars_approx)
        search_end_char   = min(len(full_text), estimated_char_end_offset + slack_chars_approx)
        search_start_char = min(search_start_char, search_end_char)

        search_start_char = min(search_start_char, len(full_text) -1) if len(full_text) > 0 else 0
        search_end_char = min(search_end_char, len(full_text))

        actual_break_char_offset = _find_natural_break_point(full_text, search_start_char, search_end_char)
        actual_break_char_offset = max(current_char_idx + 1 if current_char_idx < len(full_text) -1 else len(full_text) , actual_break_char_offset)
        actual_break_char_offset = min(actual_break_char_offset, len(full_text))

        chunk_text = full_text[current_char_idx:actual_break_char_offset].strip()

        num_words_in_chunk = 0
        if chunk_text:
            num_words_in_chunk = len(re.findall(r'\b\w+\b', chunk_text))

        if num_words_in_chunk >= MIN_CHUNK_SIZE_WORDS:
            chunks.append(chunk_text)
            print(f"Created chunk {len(chunks)}: ~{num_words_in_chunk} words, {len(chunk_text)} chars. Ends: '...{chunk_text[-50:] if len(chunk_text)>50 else chunk_text}'")
        elif chunks and num_words_in_chunk > 0:
            chunks[-1] += "\n\n" + chunk_text
            print(f"Appended small leftover ({num_words_in_chunk} words) to previous chunk.")
        elif num_words_in_chunk > 0 :
            chunks.append(chunk_text)
            print(f"Created a single small chunk {len(chunks)}: ~{num_words_in_chunk} words, {len(chunk_text)} chars.")

        # Update for next iteration: count how many word_tokens were effectively consumed.
        # This is an approximation to advance processed_words_count.
        # A more accurate way is to count words in the created chunk_text if it's not empty.
        if actual_break_char_offset > current_char_idx : # If we made progress
            consumed_text_len = actual_break_char_offset - current_char_idx
            temp_consumed_chars = 0
            words_advanced_this_iteration = 0
            for k_idx in range(processed_words_count, len(word_tokens)):
                temp_consumed_chars += len(word_tokens[k_idx])
                words_advanced_this_iteration += 1
                if temp_consumed_chars >= consumed_text_len:
                    break
            processed_words_count += words_advanced_this_iteration
        elif current_char_idx < len(full_text): # No progress, but not at end, force advance char_idx to avoid infinite loop on strange text
             actual_break_char_offset = current_char_idx + 1 # Minimal advance

        current_char_idx = actual_break_char_offset

        if current_char_idx >= len(full_text):
            break

    print(f"--- Finished creating {len(chunks)} major chunks. --- (" + str(len(word_tokens)) +" tokens)")
    return chunks

async def _process_single_chunk_for_scenes(text_chunk: str, chunk_index: int) -> List[Scene]:
    """Wraps the call to split_text_into_scenes_logic for a single chunk with logging."""
    print(f"--- Processing Major Chunk {chunk_index + 1} for scenes ({len(text_chunk)} chars, ~{len(re.findall(r'\b\w+\b', text_chunk))} words) ---")
    if not text_chunk.strip():
        print(f"Major Chunk {chunk_index + 1} is empty or whitespace only, skipping.")
        return []
    try:
        print(f"    Calling LLM to identify scenes within Major Chunk {chunk_index + 1}. This may take some time...")
        scene_response = await split_text_into_scenes_logic(text_chunk)
        print(f"    LLM processing for Major Chunk {chunk_index + 1} complete.")
        print(f"Major Chunk {chunk_index + 1} processing yielded {len(scene_response.scenes)} scenes.")
        return scene_response.scenes
    except HTTPException as e:
        print(f"HTTPException while processing Major Chunk {chunk_index + 1}: {e.detail}. Skipping this chunk.")
        return []
    except Exception as e:
        print(f"Unexpected error while processing Major Chunk {chunk_index + 1}: {str(e)}. Skipping this chunk.")
        return []


def _parse_llm_yes_no_response(llm_response_content: str) -> bool:
    """Parses a simple 'Yes' or 'No' (case-insensitive) from LLM response."""
    # Remove potential markdown/formatting and strip whitespace
    cleaned_response = llm_response_content.lower().strip().replace("`", "").replace("'", "").replace("\"", "")
    if cleaned_response == "yes":
        return True
    elif cleaned_response == "no":
        return False
    else:
        print(f"Warning: LLM Yes/No response was ambiguous or unexpected: '{llm_response_content}'. Defaulting to 'No'.")
        return False # Default to not merging if response is unclear

def _build_boundary_check_prompt(scene_a: Scene, scene_b: Scene) -> str:
    """Builds the prompt to ask LLM if two scenes should be merged."""
    return f"""
Sei un esperto analista letterario. Ti vengono fornite le descrizioni di due scene: Scena A (fine del segmento precedente) e Scena B (inizio del segmento corrente).

Il tuo compito è determinare se la Scena B è una continuazione diretta o la seconda metà della Scena A. Considera se condividono personaggi principali, ambientazione, azione continuativa e focus narrativo, suggerendo che dovrebbero essere una singola scena unificata.

Scena A (Fine del segmento precedente):
Elementi Narrativi: {scene_a.elementi_narrativi}
Personaggi: {scene_a.personaggi}
Ambientazione: {scene_a.ambientazione}
Mood/Vibe: {scene_a.mood_vibe}
Azione in corso: {scene_a.azione_in_corso}

Scena B (Inizio del segmento corrente):
Elementi Narrativi: {scene_b.elementi_narrativi}
Personaggi: {scene_b.personaggi}
Ambientazione: {scene_b.ambientazione}
Mood/Vibe: {scene_b.mood_vibe}
Azione in corso: {scene_b.azione_in_corso}

La Scena B è una continuazione diretta o la seconda metà della Scena A, il che significa che idealmente dovrebbero essere unite in una singola scena? Rispondi con un semplice 'Yes' o 'No'.
"""

def _build_merge_scenes_prompt(scene_a: Scene, scene_b: Scene) -> str:
    """Builds the prompt to ask LLM to merge two scene descriptions."""
    return f"""
Sei un esperto analista letterario. Ti vengono fornite le descrizioni di due parti di quella che dovrebbe essere una singola scena continua. La Scena A è la prima parte e la Scena B è la seconda parte.
Per favore, sintetizza queste due parti in una singola descrizione di scena coerente. Combina i loro elementi narrativi, personaggi, ambientazione, mood e azione in una descrizione unificata per la scena completa.

Scena A (Prima Parte):
Elementi Narrativi: {scene_a.elementi_narrativi}
Personaggi: {scene_a.personaggi}
Ambientazione: {scene_a.ambientazione}
Mood/Vibe: {scene_a.mood_vibe}
Azione in corso: {scene_a.azione_in_corso}

Scena B (Seconda Parte):
Elementi Narrativi: {scene_b.elementi_narrativi}
Personaggi: {scene_b.personaggi}
Ambientazione: {scene_b.ambientazione}
Mood/Vibe: {scene_b.mood_vibe}
Azione in corso: {scene_b.azione_in_corso}

Fornisci la descrizione della scena combinata come un oggetto JSON con i seguenti campi: "elementi_narrativi", "personaggi", "ambientazione", "mood_vibe", "azione_in_corso".
Restituisci SOLO l'oggetto JSON, senza testo aggiuntivo, spiegazioni o markdown.
"""

async def process_large_text(full_text: str, target_chunk_size_words: int, word_slack: int) -> ScenesResponse:
    print(f"=== Starting to process large text ({len(full_text)} chars) ===")
    major_chunks = _create_non_overlapping_major_chunks(full_text, target_chunk_size_words, word_slack)

    if not major_chunks:
        print("No major chunks were created from the input text.")
        return ScenesResponse(scenes=[])

    all_chunks_scenes: List[List[Scene]] = []
    for i, chunk_text in enumerate(major_chunks):
        scenes_from_chunk = await _process_single_chunk_for_scenes(chunk_text, i)
        all_chunks_scenes.append(scenes_from_chunk)

    if not any(all_chunks_scenes): # Check if all sublists are empty or the main list is empty
        print("No scenes were generated from any chunk.")
        return ScenesResponse(scenes=[])

    # --- LLM-Powered Boundary Merging ---
    print(f"--- Starting LLM-Powered Boundary Scene Merging --- ")
    final_merged_scenes: List[Scene] = []

    # Add scenes from the first chunk directly if it exists and is not empty
    if all_chunks_scenes and all_chunks_scenes[0]:
        final_merged_scenes.extend(all_chunks_scenes[0])
        print(f"Added {len(all_chunks_scenes[0])} scenes from chunk 1 to final list.")
    elif all_chunks_scenes: # First chunk was empty
        print("Chunk 1 had no scenes.")

    for i in range(1, len(all_chunks_scenes)):
        current_chunk_scenes = all_chunks_scenes[i]
        print(f"Processing boundary between end of (merged) Chunk {i} output and start of Chunk {i+1} output ({len(current_chunk_scenes)} scenes).")

        if not final_merged_scenes:
            print(f"No scenes in final list to compare with Chunk {i+1}. Appending {len(current_chunk_scenes)} scenes from Chunk {i+1} directly.")
            final_merged_scenes.extend(current_chunk_scenes)
            continue

        if not current_chunk_scenes:
            print(f"Chunk {i+1} has no scenes. Nothing to merge or append.")
            continue

        last_scene_from_final_list = final_merged_scenes[-1]
        first_scene_from_current_chunk = current_chunk_scenes[0]

        print(f"  Boundary Check: Comparing last scene of merged output with first scene of Chunk {i+1}.")
        # print(f"    Scene A (end of previous): {last_scene_from_final_list}") # Potentially too verbose
        # print(f"    Scene B (start of current): {first_scene_from_current_chunk}")

        boundary_check_prompt = _build_boundary_check_prompt(last_scene_from_final_list, first_scene_from_current_chunk)
        system_message_boundary = "You are a literary expert good at comparing scene descriptions."

        try:
            print("    Calling LLM for boundary merge decision...")
            boundary_llm_response_content = await _call_llm(client, boundary_check_prompt, system_message_boundary, DEFAULT_MODEL)
            print(f"    LLM (Boundary Check) Response: '{boundary_llm_response_content}'")
            should_merge = _parse_llm_yes_no_response(boundary_llm_response_content)

            if should_merge:
                print(f"    Decision: Merge. Calling LLM to combine scenes.")
                merge_prompt = _build_merge_scenes_prompt(last_scene_from_final_list, first_scene_from_current_chunk)
                system_message_merge = "You are an expert literary analyst skilled at synthesizing scene descriptions into JSON."

                merged_scene_llm_content = await _call_llm(client, merge_prompt, system_message_merge, DEFAULT_MODEL)
                print(f"    LLM (Merge Scene) Raw JSON Output (first 500 chars): {merged_scene_llm_content[:500]}...")

                # Parse the merged scene JSON
                try:
                    # It's possible the LLM doesn't wrap in [], so _get_json_payload might not be needed if prompt is strict
                    # Assuming the merge prompt asks for a single JSON *object*
                    merged_scene_data = json.loads(merged_scene_llm_content)
                    merged_scene_obj = Scene(**merged_scene_data)

                    final_merged_scenes[-1] = merged_scene_obj # Replace the last scene
                    print(f"    Successfully merged Scene A and Scene B. Updated last scene in final list.")
                    # Append the rest of the scenes from the current chunk
                    if len(current_chunk_scenes) > 1:
                        final_merged_scenes.extend(current_chunk_scenes[1:])
                        print(f"    Appended remaining {len(current_chunk_scenes) - 1} scenes from Chunk {i+1}.")
                    else:
                        print(f"    No remaining scenes in Chunk {i+1} after merging its first scene.")
                except (json.JSONDecodeError, ValidationError, TypeError) as e_merge_parse:
                    print(f"    ERROR: Failed to parse or validate merged scene JSON from LLM: {str(e_merge_parse)}. LLM output: {merged_scene_llm_content[:500]}...")
                    print(f"    Fallback: Not merging. Appending all {len(current_chunk_scenes)} scenes from Chunk {i+1} separately.")
                    final_merged_scenes.extend(current_chunk_scenes)

            else: # Should not merge
                print(f"    Decision: Do not merge. Appending all {len(current_chunk_scenes)} scenes from Chunk {i+1} separately.")
                final_merged_scenes.extend(current_chunk_scenes)

        except HTTPException as http_e_boundary:
            print(f"    ERROR: HTTPException during boundary/merge LLM call for Chunk {i+1}: {http_e_boundary.detail}. Appending scenes without merge.")
            final_merged_scenes.extend(current_chunk_scenes)
        except Exception as e_boundary_unhandled:
            print(f"    ERROR: Unexpected error during boundary/merge logic for Chunk {i+1}: {str(e_boundary_unhandled)}. Appending scenes without merge.")
            final_merged_scenes.extend(current_chunk_scenes)

    print(f"--- Total scenes after LLM-Powered Boundary Merging: {len(final_merged_scenes)} ---")
    return ScenesResponse(scenes=final_merged_scenes)

@app.post("/split-scenes", response_model=ScenesResponse)
async def split_text_into_scenes(input_data: TextInput):
    """
    Splits text into individual scenes. Handles large texts by chunking.
    """
    # Simple heuristic: if text is very long, use the chunking process.
    # Otherwise, use the direct method (which is now wrapped in _process_single_chunk_for_scenes if we call it directly)
    # For now, let's always use process_large_text to test the chunking.
    # A more sophisticated length check can be added later.
    print(f"Received text for scene splitting, length: {len(input_data.text)} chars.")
    if len(input_data.text) == 0:
        return ScenesResponse(scenes=[])

    # Use the new large text processing logic
    return await process_large_text(input_data.text, TARGET_CHUNK_SIZE_WORDS, WORD_COUNT_SLACK)


@app.get("/")
async def root():
    return {"message": "Text Chunker API - Split fiction into scenes"}


async def main():
    from pathlib import Path
    with open(Path(__file__).parent / "text.txt", "r", encoding="utf-8") as file:
        text = file.read()

    # text2 = """
    # Once upon a time, in a small village nestled between rolling hills and a whispering forest, there lived a young baker named Elena. Every morning before dawn, she would rise to knead dough and fill her shop with the warm aroma of fresh bread.

    # One particularly misty morning, as Elena was preparing her usual loaves, she noticed something peculiar. The flour she had been using seemed to shimmer with an otherworldly light. At first, she thought it was merely a trick of the candlelight, but as she worked the dough, it began to glow more brightly.

    # When the first customer arrived—old Mr. Henrick, who came every day for his daily baguette—Elena hesitantly offered him a loaf made from the mysterious flour. To her amazement, as soon as he took a bite, his weathered face seemed to smooth, and his tired eyes sparkled with renewed vigor.

    # Word spread quickly through the village about Elena's magical bread. People came from far and wide, hoping to taste the miraculous loaves that could restore youth and vitality. But Elena soon discovered that the magic came with a price—each loaf she baked took a little of her own life force.

    # Faced with this terrible choice, Elena had to decide: continue using her gift to help others at the cost of her own life, or keep the secret to herself and watch her neighbors age and suffer. In the end, she chose compassion over self-preservation, becoming a legend that would be told for generations to come.
    # """

    response = await split_text_into_scenes(TextInput(text=text))
    pprint(response.scenes)


if __name__ == "__main__":
    asyncio.run(main())
