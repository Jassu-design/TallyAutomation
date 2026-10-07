import React from 'react';
import { getStatusBadge } from '../../utils/formatters';
import { CheckCircle2, AlertTriangle, AlertCircle, Clock, Copy, ArrowUpRight } from 'lucide-react';

export default function Badge({ status }) {
  const badgeInfo = getStatusBadge(status);
  const s = (status || '').toUpperCase();

  let Icon = null;
  if (s === 'POSTED' || s === 'APPROVED') Icon = CheckCircle2;
  else if (s === 'REVIEW_REQUIRED') Icon = AlertTriangle;
  else if (s === 'FAILED' || s === 'REJECTED') Icon = AlertCircle;
  else if (s === 'DUPLICATE') Icon = Copy;
  else if (s === 'POSTING') Icon = ArrowUpRight;
  else Icon = Clock;

  return (
    <span className={`badge ${badgeInfo.className}`}>
      {Icon && <Icon size={12} />}
      {badgeInfo.label}
    </span>
  );
}
