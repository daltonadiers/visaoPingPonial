import "./VideoFeed.css";

interface VideoFeedProps {
  streamUrl: string;
}

export default function VideoFeed({ streamUrl }: VideoFeedProps) {
  return (
    <div className="video-section">
      <h2>Transmissão ao vivo</h2>
      <div className="video-container">
        <img src={streamUrl} alt="Feed da câmera" />
      </div>
    </div>
  );
}
