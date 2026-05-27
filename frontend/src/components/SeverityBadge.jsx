export default function SeverityBadge({ severity }) {
  const sev = (severity || 'UNKNOWN').toUpperCase();

  const getStyleClass = () => {
    switch (sev) {
      case 'CRITICAL':
        return 'badge-critical';
      case 'HIGH':
        return 'badge-high';
      case 'MEDIUM':
        return 'badge-medium';
      case 'LOW':
        return 'badge-low';
      case 'NONE':
        return 'badge-success';
      default:
        return 'badge-low';
    }
  };

  return (
    <span className={`badge ${getStyleClass()}`}>
      {sev}
    </span>
  );
}
