import { useState, useEffect } from "react";
import Scoreboard from "./components/Scoreboard";
import VideoFeed from "./components/VideoFeed";
import StatusBar from "./components/StatusBar";
import "./App.css";

const API_URL = "http://localhost:8000";

export default function App() {
  const [playerA, setPlayerA] = useState("Jogador A");
  const [playerB, setPlayerB] = useState("Jogador B");
  const [scoreA, setScoreA] = useState(0);
  const [scoreB, setScoreB] = useState(0);
  const [statusMsg, setStatusMsg] = useState("Em andamento");

  // polling a cada 200ms para o estado do backend
  useEffect(() => {
    const interval = setInterval(() => {
      fetch(`${API_URL}/state`)
        .then((res) => res.json())
        .then((data) => {
          setPlayerA(data.playerA);
          setPlayerB(data.playerB);
          setScoreA(data.scoreA);
          setScoreB(data.scoreB);
          setStatusMsg(data.message);
        })
        .catch(() => {
          setStatusMsg("Falha ao conectar com o servidor");
        });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const handleReset = () => {
    fetch(`${API_URL}/reset`, { method: "POST" })
      .then(() => {
        setStatusMsg("Partida reiniciada");
        setScoreA(0);
        setScoreB(0);
      })
      .catch(() => setStatusMsg("Erro ao resetar"));
  };

  return (
    <div className="app">
      <h1 className="title">PingPong Vision</h1>

      <div className="score-container">
        <Scoreboard player={playerA} score={scoreA} />
        <Scoreboard player={playerB} score={scoreB} />
      </div>

      <VideoFeed streamUrl={`${API_URL}/video_feed`} />
      <StatusBar message={statusMsg} />

      <button className="reset-btn" onClick={handleReset}>
        Resetar partida
      </button>
    </div>
  );
}
