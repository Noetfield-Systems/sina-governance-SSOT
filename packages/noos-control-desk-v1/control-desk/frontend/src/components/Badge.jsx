export default function Badge({ verdict }) {
  if (!verdict || verdict === 'TODO') {
    return <span className="badge todo">TODO</span>;
  }
  const cls =
    verdict === 'PASS' ? 'pass' : verdict === 'BLOCKED' ? 'blocked' : 'fail';
  return <span className={`badge ${cls}`}>{verdict}</span>;
}
