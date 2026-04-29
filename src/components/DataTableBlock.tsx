import { useDataModel } from "../hooks/useDataModel";
import "./DataTableBlock.css";

interface DataTableBlockProps {
  columns?: any;
  rows?: any;
}

export function DataTableBlock({ columns, rows }: DataTableBlockProps) {
  const { resolve } = useDataModel();
  const resolvedColumns: string[] = resolve(columns) ?? [];
  const resolvedRows: any[][] = resolve(rows) ?? [];

  if (!resolvedColumns.length) {
    return <div className="data-table-empty">데이터 없음</div>;
  }

  return (
    <div className="data-table-wrapper">
      <table className="data-table">
        <thead>
          <tr>
            {resolvedColumns.map((col: string, i: number) => (
              <th key={i}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {resolvedRows.map((row: any[], i: number) => (
            <tr key={i}>
              {row.map((cell: any, j: number) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
