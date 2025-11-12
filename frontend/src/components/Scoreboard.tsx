import "./ScoreBoard.css";

interface ScoreboardProps {
  player: string;
  setPlayer: React.Dispatch<React.SetStateAction<string>>;
  score: number;
}

export default function Scoreboard({ player, setPlayer, score }: ScoreboardProps) {
  return (
    <div className="scoreboard">
      <input
        className="player-name"
        type="text"
        value={player}
        onChange={(e) => setPlayer(e.target.value)}
      />
      <div className="score">{score}</div>
    </div>
  );
}
