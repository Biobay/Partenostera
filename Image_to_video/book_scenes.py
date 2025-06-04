#!/usr/bin/env python3
"""
File di esempio per integrare le scene del tuo compagno
Sostituisci questo con l'output del sistema del tuo compagno
"""

from scene_parser import Scene

# ESEMPIO: Scene generate dal sistema del tuo compagno
# Sostituisci questa lista con l'output del suo sistema
book_scenes = [
    Scene(
        elementi_narrativi='Pane fresco, impasto, forno, arredo semplice di una panetteria del villaggio.',
        personaggi="Elena: una giovane panettiera, con mani forse un po' infuocate, viso concentrato ma tranquillo, espressione diligente.",
        ambientazione="Un piccolo villaggio tra colline ondulate e una foresta sussurrante. L'interno di una panetteria accogliente, prima dell'alba, con una luce soffusa e un'atmosfera calda, permeata dall'aroma del pane.",
        mood_vibe='Calmo, laborioso, confortante, tradizionale.',
        azione_in_corso="Elena si alza prima dell'alba e impasta il pane, riempiendo il suo negozio con il caldo aroma del pane fresco."
    ),
    Scene(
        elementi_narrativi='Farina che luccica con una luce ultraterrena, ciotole, strumenti da panettiere, candele tremolanti.',
        personaggi="Elena: viso sorpreso e curioso, occhi aperti, un po' scettica inizialmente, poi profondamente incuriosita e meravigliata.",
        ambientazione="L'interno della panetteria di Elena, una mattina particolarmente nebbiosa. La luce delle candele è l'unica fonte, rendendo l'ambiente misterioso e suggestivo.",
        mood_vibe='Misterioso, curioso, soprannaturale, di scoperta.',
        azione_in_corso='Elena sta preparando il suo solito pane quando nota la farina luccicare e brillare sempre più intensamente mentre la lavora.'
    ),
    Scene(
        elementi_narrativi='Un filone di pane appena sfornato, il bancone della panetteria, piccole monete (facoltative).',
        personaggi="Elena: titubante mentre offre il pane, poi sbalordita; il vecchio Signor Henrick: inizialmente con un viso 'increspato' e occhi stanchi, che si trasformano immediatamente in un viso più liscio e occhi che brillano di rinnovato vigore e giovinezza.",
        ambientazione="La panetteria di Elena, durante l'orario di apertura del mattino, con la luce che filtra dall'esterno. L'ambiente è caldo e invitante.",
        mood_vibe='Miracoloso, sorprendente, speranzoso, di stupore.',
        azione_in_corso='Elena offre un pane fatto con la farina misteriosa al Signor Henrick, che lo morde e sperimenta una trasformazione visibile e immediata.'
    ),
    Scene(
        elementi_narrativi='Forno, pasta, una sensazione di stanchezza o un leggero pallore sul viso di Elena.',
        personaggi="Elena: visibilmente affaticata o con un'ombra di preoccupazione sul viso, gli occhi che riflettono una nuova consapevolezza, sola o in un momento di introspezione.",
        ambientazione="La panetteria di Elena, forse nel tardo pomeriggio o la sera, dopo una giornata intensa. L'ambiente è più buio o ha una luce più fioca, riflettendo il mood. Potrebbe esserci un disordine creativo di farina e utensili.",
        mood_vibe='Grave, di realizzazione, proccupato, di tristezza.',
        azione_in_corso="Elena si rende conto, forse mentre impasta o dopo aver infornato l'ennesimo pane, che ogni pagnotta magica le sottrae un po' della sua forza vitale."
    ),
    Scene(
        elementi_narrativi="Nessun elemento narrativo specifico, l'attenzione è tutta sulla persona e la sua scelta.",
        personaggi='Elena: una figura decisa ma pensierosa, il suo viso mostra il peso della scelta ma anche una profonda compassione e risolutezza. Potrebbe avere le mani giunte o essere in una posa di profonda riflessione.',
        ambientazione="Un luogo intimo e quieto, come l'angolo tranquillo della sua panetteria o la sua semplice camera da letto, nella penombra. L'ambiente dovrebbe trasmettere solitudine e gravità.",
        mood_vibe='Solenne, coraggioso, pesante, di profonda compassione, di risoluzione.',
        azione_in_corso='Elena è immobile, persa nei suoi pensieri, mentre prende una difficile e altruistica decisione: continuare a usare il suo dono per aiutare gli altri, anche se ciò le costerà la vita stessa.'
    )
]

def get_book_scenes():
    """
    Funzione che restituisce le scene del libro
    SOSTITUISCI questa funzione con l'integrazione del codice del tuo compagno
    """
    return book_scenes

if __name__ == "__main__":
    scenes = get_book_scenes()
    print(f"Caricate {len(scenes)} scene dal libro")
    for i, scene in enumerate(scenes, 1):
        print(f"Scena {i}: {scene.azione_in_corso[:50]}...")
