### Informazioni per il task
Gli URL di radio streaming possono essere analizzati tramite strumenti di rete e lettori multimediali, 
per identificare il formato del flusso audio, anche quando l'estensione non è esplicita. 

### Classificazione
Protocollo (HTTP, RTMP, HLS)
Formato audio (MP3, AAC, OGG)
Supporto metadati (Icecast/Shoutcast)

**Tipi di flussi e protocolli comuni**
Protocollo / Formato	Descrizione	Estensione / Indicatore
- Icecast / Shoutcast	Streaming MP3/AAC con metadati	Nessuna estensione, header HTTP
- HLS (HTTP Live Streaming)	Segmenti .ts e playlist .m3u8	.m3u8
- RTMP / RTSP	Streaming in tempo reale	URL con rtmp:// o rtsp://
- Direct MP3/AAC	Flusso diretto	.mp3, .aac, .ogg
- Playlist M3U / PLS	Contiene URL del flusso	.m3u, .pls
- Lettori multimediali come VLC o ffmpeg:

### Come analizzare un URL di streaming radio
Quando l'url ha un’`estensione esplicita` (.mp3, .aac, .m3u, .pls), viene automaticamente accettato e classificato rispetto al tipo. Queste tipologie sono mantenute in un entità del sistema da sviluppare (`RadioCh - radio Channels`)
Quando l'url non ha estensione esplicita si analizza il flusso (es http://sc8.radiocaroline.net:8020/'), ci sono tre opzioni:
Per esempio: ttps://bcradio-live-a.edge.audiocdn.com/10003_64k.aac (direct MP3/AAC)

Quando l'url non ha estensione esplicita si analizza il flusso (es http://sc8.radiocaroline.net:8020/'), ci sono tre opzioni:
- catturare l'header ed il content-type e verificare se si riesce a risalire a un tipo conosciuto
- analizzare l'url con `ffmpeg -i` 
- o com `curl -I`, nel caso di esempio abbiamo:

ffmpeg: `Stream #0:0: Audio: mp3 (mp3float), 22050 Hz, mono, fltp, 24 kb/s`
curl:   `content-type:audio/mpeg`

### Per approfondire
Radio Browser – aggregatore open source con API e esportazione M3U
Maccanismi – Elenco URL streaming radio italiane – guida tecnica su come trovare e analizzare URL radio
Infomaniak – Metadati nei flussi audio – utile per chi vuole trasmettere o ricevere metadati (titolo brano, artista)
Mauro Graziani – Formati audio digitali – analisi approfondita dei formati audio e loro caratteristiche tecniche
