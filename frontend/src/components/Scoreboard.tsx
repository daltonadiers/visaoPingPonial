import "./ScoreBoard.css";

interface ScoreboardProps {
  player: string;
  score: number;
}

export default function Scoreboard({ player, score }: ScoreboardProps) {
  return (
    <div className="scoreboard">
      <div className="player-name">{player}</div>
      <div className="score">{score}</div>
    </div>
  );
}
