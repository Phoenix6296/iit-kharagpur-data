// components/MetricsTable.jsx
"use client";

export const MetricsTable = ({ evaluationMetrics }) => (
  <div className="bg-white shadow-lg rounded-lg p-6 w-full max-w-md mt-6">
    <h2 className="text-xl font-semibold text-gray-700 mb-4">
      Model Evaluation Metrics
    </h2>
    <table className="w-full border-collapse border border-gray-300">
      <thead>
        <tr className="bg-gray-200">
          <th className="border border-gray-300 p-2 text-left">Metric</th>
          <th className="border border-gray-300 p-2 text-left">Value</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(evaluationMetrics).map(([key, value]) => (
          <tr key={key} className="odd:bg-white even:bg-gray-100">
            <td className="border border-gray-300 p-2">{key}</td>
            <td className="border border-gray-300 p-2 font-semibold">
              {typeof value === "number" ? value.toFixed(4) : value}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);
