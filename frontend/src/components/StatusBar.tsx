import "./StatusBar.css";

interface StatusBarProps {
  message: string;
}

export default function StatusBar({ message }: StatusBarProps) {
  return (
    <div className="status-bar">
      <p>{message}</p>
    </div>
  );
}
