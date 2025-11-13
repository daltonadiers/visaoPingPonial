import { useState, useEffect, useRef } from "react";
import Scoreboard from "./components/Scoreboard";
import VideoFeed from "./components/VideoFeed";
import StatusBar from "./components/StatusBar";
import "./App.css";
import confetti from "canvas-confetti";

const API_URL = "http://localhost:8000";

export default function App() {
  const [playerA, setPlayerA] = useState("Jogador A");
  const [playerB, setPlayerB] = useState("Jogador B");
  const [scoreA, setScoreA] = useState(0);
  const [scoreB, setScoreB] = useState(0);
  const [statusMsg, setStatusMsg] = useState("Em andamento");
  const hasWinnerRef = useRef(false);

  useEffect(() => {
    const interval = setInterval(() => {
      fetch(`${API_URL}/state`)
        .then((res) => res.json())
        .then((data) => {
          setPlayerA(data.playerA);
          setPlayerB(data.playerB);
          setScoreA(data.scoreA);
          setScoreB(data.scoreB);

          if (!hasWinnerRef.current) {
            if (data.scoreA >= 7 || data.scoreB >= 7) {
              hasWinnerRef.current = true;
              const winnerName = data.scoreA >= 7 ? data.playerA : data.playerB;
              setStatusMsg(`${winnerName} venceu!`);
              confetti({ particleCount: 200, spread: 90, origin: { y: 0.6 } });
            } else {
              setStatusMsg(data.message);
            }
          }
        })
        .catch(() => {
          if (!hasWinnerRef.current) {
            setStatusMsg("Falha ao conectar com o servidor");
          }
        });
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const handleReset = () => {
    fetch(`${API_URL}/reset`, { method: "POST" })
      .then(() => {
        hasWinnerRef.current = false;
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
