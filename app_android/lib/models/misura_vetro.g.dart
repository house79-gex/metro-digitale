// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'misura_vetro.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MisuraVetro _$MisuraVetroFromJson(Map<String, dynamic> json) => MisuraVetro(
      larghezzaRaw: (json['larghezza_raw'] as num).toDouble(),
      altezzaRaw: (json['altezza_raw'] as num).toDouble(),
      larghezzaNetta: (json['larghezza_netta'] as num).toDouble(),
      altezzaNetta: (json['altezza_netta'] as num).toDouble(),
      materiale: json['materiale'] as String,
      quantita: json['quantita'] as int,
      gioco: (json['gioco'] as num).toDouble(),
      timestamp: json['timestamp'] == null
          ? null
          : DateTime.parse(json['timestamp'] as String),
    );

Map<String, dynamic> _$MisuraVetroToJson(MisuraVetro instance) =>
    <String, dynamic>{
      'larghezza_raw': instance.larghezzaRaw,
      'altezza_raw': instance.altezzaRaw,
      'larghezza_netta': instance.larghezzaNetta,
      'altezza_netta': instance.altezzaNetta,
      'materiale': instance.materiale,
      'quantita': instance.quantita,
      'gioco': instance.gioco,
      'timestamp': instance.timestamp.toIso8601String(),
    };
