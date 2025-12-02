import 'package:json_annotation/json_annotation.dart';

part 'misura_vetro.g.dart';

@JsonSerializable()
class MisuraVetro {
  final double larghezzaRaw;
  final double altezzaRaw;
  final double larghezzaNetta;
  final double altezzaNetta;
  final String materiale;
  final int quantita;
  final double gioco;
  final DateTime timestamp;

  MisuraVetro({
    required this.larghezzaRaw,
    required this.altezzaRaw,
    required this.larghezzaNetta,
    required this.altezzaNetta,
    required this.materiale,
    required this.quantita,
    required this.gioco,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  // Factory da JSON Bluetooth
  factory MisuraVetro.fromJson(Map<String, dynamic> json) =>
      _$MisuraVetroFromJson(json);

  Map<String, dynamic> toJson() => _$MisuraVetroToJson(this);

  // Copia con modifica quantità
  MisuraVetro copyWith({
    double? larghezzaRaw,
    double? altezzaRaw,
    double? larghezzaNetta,
    double? altezzaNetta,
    String? materiale,
    int? quantita,
    double? gioco,
    DateTime? timestamp,
  }) {
    return MisuraVetro(
      larghezzaRaw: larghezzaRaw ?? this.larghezzaRaw,
      altezzaRaw: altezzaRaw ?? this.altezzaRaw,
      larghezzaNetta: larghezzaNetta ?? this.larghezzaNetta,
      altezzaNetta: altezzaNetta ?? this.altezzaNetta,
      materiale: materiale ?? this.materiale,
      quantita: quantita ?? this.quantita,
      gioco: gioco ?? this.gioco,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  // Calcola similarità per raggruppamento
  bool isSimilarTo(MisuraVetro other, double tolerance) {
    return (larghezzaRaw - other.larghezzaRaw).abs() <= tolerance &&
        (altezzaRaw - other.altezzaRaw).abs() <= tolerance &&
        materiale == other.materiale;
  }

  @override
  String toString() {
    return 'MisuraVetro(L: ${larghezzaNetta.toStringAsFixed(1)}mm x H: ${altezzaNetta.toStringAsFixed(1)}mm, Mat: $materiale, Q: $quantita)';
  }
}
