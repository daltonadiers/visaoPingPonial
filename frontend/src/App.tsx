import { useState } from "react";
import Scoreboard from "./components/Scoreboard";
import VideoFeed from "./components/VideoFeed";
import StatusBar from "./components/StatusBar";
import "./App.css";

export default function App() {
  const [playerA, setPlayerA] = useState("Jogador A");
  const [playerB, setPlayerB] = useState("Jogador B");
  const [scoreA, setScoreA] = useState(0);
  const [scoreB, setScoreB] = useState(0);
  const [statusMsg, setStatusMsg] = useState("Em andamento");

  const handleReset = () => {
    setPlayerA("Jogador A");
    setPlayerB("Jogador B");
    setScoreA(0);
    setScoreB(0);
    setStatusMsg("Em andamento");
  };

  return (
    <div className="app">
      <h1 className="title">PingPong Vision</h1>

      <div className="score-container">
        <Scoreboard player={playerA} score={scoreA} setPlayer={setPlayerA} />
        <Scoreboard player={playerB} score={scoreB} setPlayer={setPlayerB} />
      </div>

      <VideoFeed />

      <StatusBar message={statusMsg} />

      <button className="reset-btn" onClick={handleReset}>
        Resetar partida
      </button>
    </div>
  );
}
