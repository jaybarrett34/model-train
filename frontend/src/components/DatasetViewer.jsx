import { useState } from 'react';
import { ChevronLeft, ChevronRight, Copy, CheckCircle } from 'lucide-react';

const DatasetViewer = ({ dataset, samples, onClose }) => {
  const [currentPage, setCurrentPage] = useState(0);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const samplesPerPage = 10;

  const totalPages = Math.ceil(samples.length / samplesPerPage);
  const startIndex = currentPage * samplesPerPage;
  const endIndex = Math.min(startIndex + samplesPerPage, samples.length);
  const currentSamples = samples.slice(startIndex, endIndex);

  const handleCopy = (sample, index) => {
    const text = JSON.stringify(sample, null, 2);
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handlePrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-white rounded-lg w-full max-w-5xl max-h-[90vh] mx-4 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{dataset.name}</h2>
            <p className="text-sm text-gray-600 mt-1">
              Showing {startIndex + 1} - {endIndex} of {samples.length} samples
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-4">
            {currentSamples.map((sample, idx) => {
              const globalIndex = startIndex + idx;
              return (
                <div key={globalIndex} className="border border-gray-200 rounded-lg bg-gray-50">
                  <div className="flex justify-between items-center px-4 py-2 border-b border-gray-200 bg-gray-100">
                    <div className="flex items-center space-x-3">
                      <span className="text-sm font-semibold text-gray-700">
                        Sample {globalIndex + 1}
                      </span>
                      {sample.metadata && (
                        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                          {sample.metadata.type || 'standard'}
                        </span>
                      )}
                    </div>
                    <button
                      onClick={() => handleCopy(sample, globalIndex)}
                      className="text-sm flex items-center space-x-1 text-gray-600 hover:text-primary-600 transition-colors"
                      title="Copy to clipboard"
                    >
                      {copiedIndex === globalIndex ? (
                        <>
                          <CheckCircle size={16} className="text-green-600" />
                          <span className="text-green-600">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy size={16} />
                          <span>Copy</span>
                        </>
                      )}
                    </button>
                  </div>

                  <div className="p-4">
                    {/* Input/Output Format */}
                    {sample.input && sample.output ? (
                      <div className="space-y-3">
                        <div>
                          <div className="text-xs font-semibold text-gray-600 mb-1">INPUT:</div>
                          <div className="bg-white p-3 rounded border border-gray-200">
                            <pre className="text-sm font-mono text-gray-900 whitespace-pre-wrap">
                              {typeof sample.input === 'string'
                                ? sample.input
                                : JSON.stringify(sample.input, null, 2)}
                            </pre>
                          </div>
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-gray-600 mb-1">OUTPUT:</div>
                          <div className="bg-white p-3 rounded border border-gray-200">
                            <pre className="text-sm font-mono text-gray-900 whitespace-pre-wrap">
                              {typeof sample.output === 'string'
                                ? sample.output
                                : JSON.stringify(sample.output, null, 2)}
                            </pre>
                          </div>
                        </div>
                      </div>
                    ) : (
                      /* Raw JSON Format */
                      <pre className="text-sm font-mono text-gray-900 overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(sample, null, 2)}
                      </pre>
                    )}
                  </div>

                  {/* Quality Indicators */}
                  {sample.quality_score !== undefined && (
                    <div className="px-4 py-2 border-t border-gray-200 bg-gray-50">
                      <div className="flex items-center space-x-4 text-xs">
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-600">Quality:</span>
                          <div className="flex items-center space-x-1">
                            <div className="w-24 bg-gray-200 rounded-full h-2">
                              <div
                                className={`h-2 rounded-full ${
                                  sample.quality_score >= 0.8
                                    ? 'bg-green-600'
                                    : sample.quality_score >= 0.6
                                    ? 'bg-yellow-600'
                                    : 'bg-red-600'
                                }`}
                                style={{ width: `${sample.quality_score * 100}%` }}
                              />
                            </div>
                            <span className="font-semibold text-gray-900 w-8">
                              {(sample.quality_score * 100).toFixed(0)}%
                            </span>
                          </div>
                        </div>
                        {sample.tokens && (
                          <div className="text-gray-600">
                            Tokens: <span className="font-semibold text-gray-900">{sample.tokens}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer with Pagination */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Page {currentPage + 1} of {totalPages}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handlePrevPage}
              disabled={currentPage === 0}
              className="btn-secondary flex items-center space-x-1"
            >
              <ChevronLeft size={16} />
              <span>Previous</span>
            </button>
            <button
              onClick={handleNextPage}
              disabled={currentPage === totalPages - 1}
              className="btn-secondary flex items-center space-x-1"
            >
              <span>Next</span>
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DatasetViewer;
