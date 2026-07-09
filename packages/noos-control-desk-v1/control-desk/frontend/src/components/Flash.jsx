export default function Flash({ kind = 'ok', children }) {
  if (!children) return null;
  return <div className={`flash ${kind}`}>{children}</div>;
}
