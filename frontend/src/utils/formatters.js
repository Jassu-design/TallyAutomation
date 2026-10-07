export function formatCurrency(amount) {
  if (amount === undefined || amount === null) return '₹0.00';
  const num = typeof amount === 'number' ? amount : parseFloat(amount);
  if (isNaN(num)) return '₹0.00';
  
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(num);
}

export function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const parts = dateStr.split('-');
    if (parts.length === 3) {
      const d = new Date(parts[0], parts[1] - 1, parts[2]);
      return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
    }
    return dateStr;
  } catch (e) {
    return dateStr;
  }
}

export function getStatusBadge(status) {
  const s = (status || '').toUpperCase();
  switch (s) {
    case 'POSTED':
      return { label: 'Posted', className: 'badge-posted' };
    case 'APPROVED':
      return { label: 'Approved', className: 'badge-approved' };
    case 'REVIEW_REQUIRED':
      return { label: 'Review Required', className: 'badge-review_required' };
    case 'FAILED':
      return { label: 'Failed', className: 'badge-failed' };
    case 'DUPLICATE':
      return { label: 'Duplicate', className: 'badge-duplicate' };
    case 'POSTING':
      return { label: 'Posting...', className: 'badge-posting' };
    case 'REJECTED':
      return { label: 'Rejected', className: 'badge-rejected' };
    case 'VALIDATED':
      return { label: 'Validated', className: 'badge-validated' };
    case 'PENDING':
      return { label: 'Pending', className: 'badge-pending' };
    default:
      return { label: status || 'Imported', className: 'badge-imported' };
  }
}
