import "./VideoFeed.css";

export default function VideoFeed() {
  const placeholder =
    "https://picsum.photos/800/450?blur=3"; // imagem aleatória só para simulação

  return (
    <div className="video-section">
      <h2>Transmissão ao vivo</h2>
      <div className="video-container">
        <img src={placeholder} alt="Simulação do vídeo" />
      </div>
    </div>
  );
}
