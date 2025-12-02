import 'package:flutter/foundation.dart';
import '../models/misura_vetro.dart';

class VetriProvider with ChangeNotifier {
  final List<MisuraVetro> _misure = [];
  double _tolleranzaRaggruppamento = 2.0; // mm

  List<MisuraVetro> get misure => List.unmodifiable(_misure);
  double get tolleranzaRaggruppamento => _tolleranzaRaggruppamento;

  // Aggiungi misura con raggruppamento intelligente
  void aggiungiMisura(MisuraVetro misura) {
    // Cerca se esiste una misura simile
    final indexSimilare = _misure.indexWhere(
      (m) => m.isSimilarTo(misura, _tolleranzaRaggruppamento),
    );

    if (indexSimilare != -1) {
      // Misura simile trovata: incrementa quantità e aggiorna media
      final misuraEsistente = _misure[indexSimilare];
      final quantitaTotale = misuraEsistente.quantita + 1;

      // Calcola nuova media ponderata
      final nuovaLarghezzaRaw =
          ((misuraEsistente.larghezzaRaw * misuraEsistente.quantita) +
                  misura.larghezzaRaw) /
              quantitaTotale;
      final nuovaAltezzaRaw =
          ((misuraEsistente.altezzaRaw * misuraEsistente.quantita) +
                  misura.altezzaRaw) /
              quantitaTotale;
      final nuovaLarghezzaNetta =
          ((misuraEsistente.larghezzaNetta * misuraEsistente.quantita) +
                  misura.larghezzaNetta) /
              quantitaTotale;
      final nuovaAltezzaNetta =
          ((misuraEsistente.altezzaNetta * misuraEsistente.quantita) +
                  misura.altezzaNetta) /
              quantitaTotale;

      // Arrotonda al millimetro
      final larghezzaArrotondata = nuovaLarghezzaNetta.round().toDouble();
      final altezzaArrotondata = nuovaAltezzaNetta.round().toDouble();

      _misure[indexSimilare] = misuraEsistente.copyWith(
        larghezzaRaw: nuovaLarghezzaRaw,
        altezzaRaw: nuovaAltezzaRaw,
        larghezzaNetta: larghezzaArrotondata,
        altezzaNetta: altezzaArrotondata,
        quantita: quantitaTotale,
      );

      debugPrint(
          'Misura raggruppata: Q=$quantitaTotale, L=${larghezzaArrotondata}mm, H=${altezzaArrotondata}mm');
    } else {
      // Nuova misura: aggiungi alla lista
      final larghezzaArrotondata = misura.larghezzaNetta.round().toDouble();
      final altezzaArrotondata = misura.altezzaNetta.round().toDouble();

      _misure.add(misura.copyWith(
        larghezzaNetta: larghezzaArrotondata,
        altezzaNetta: altezzaArrotondata,
      ));

      debugPrint('Nuova misura aggiunta: ${_misure.length}');
    }

    notifyListeners();
  }

  // Rimuovi misura
  void rimuoviMisura(int index) {
    if (index >= 0 && index < _misure.length) {
      _misure.removeAt(index);
      notifyListeners();
    }
  }

  // Modifica quantità
  void modificaQuantita(int index, int nuovaQuantita) {
    if (index >= 0 && index < _misure.length && nuovaQuantita > 0) {
      _misure[index] = _misure[index].copyWith(quantita: nuovaQuantita);
      notifyListeners();
    }
  }

  // Imposta tolleranza
  void setTolleranza(double tolleranza) {
    if (tolleranza > 0) {
      _tolleranzaRaggruppamento = tolleranza;
      notifyListeners();
    }
  }

  // Svuota lista
  void svuotaMisure() {
    _misure.clear();
    notifyListeners();
  }

  // Ottieni totale vetri
  int getTotaleVetri() {
    return _misure.fold<int>(0, (sum, m) => sum + m.quantita);
  }

  // Ottieni misure raggruppate per materiale
  Map<String, List<MisuraVetro>> getMisurePerMateriale() {
    final Map<String, List<MisuraVetro>> grouped = {};
    for (final misura in _misure) {
      if (!grouped.containsKey(misura.materiale)) {
        grouped[misura.materiale] = [];
      }
      grouped[misura.materiale]!.add(misura);
    }
    return grouped;
  }
}
