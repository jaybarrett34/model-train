import { useState, useEffect } from 'react';
import { Database, Download, Trash2, CheckCircle, XCircle, Eye } from 'lucide-react';
import { datasetsApi } from '../services/api';
import useStore from '../store/useStore';
import { formatDate, formatBytes } from '../utils/helpers';

const DatasetManager = () => {
  const { currentProject, datasets, setDatasets } = useStore();
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [validationResults, setValidationResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  useEffect(() => {
    if (currentProject) {
      loadDatasets();
    }
  }, [currentProject]);

  const loadDatasets = async () => {
    if (!currentProject) return;

    try {
      setLoading(true);
      const response = await datasetsApi.list(currentProject.id);
      setDatasets(response.data);
    } catch (error) {
      console.error('Failed to load datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleValidateDataset = async (datasetId) => {
    try {
      const response = await datasetsApi.validate(currentProject.id, datasetId);
      setValidationResults(response.data);
    } catch (error) {
      console.error('Failed to validate dataset:', error);
      alert('Failed to validate dataset');
    }
  };

  const handleExportDataset = async (datasetId, format) => {
    try {
      const response = await datasetsApi.export(currentProject.id, datasetId, format);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dataset.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Failed to export dataset:', error);
      alert('Failed to export dataset');
    }
  };

  const handleDeleteDataset = async (datasetId) => {
    if (!confirm('Are you sure you want to delete this dataset?')) return;

    try {
      await datasetsApi.delete(currentProject.id, datasetId);
      setDatasets(datasets.filter(d => d.id !== datasetId));
    } catch (error) {
      console.error('Failed to delete dataset:', error);
      alert('Failed to delete dataset');
    }
  };

  const handlePreviewDataset = async (dataset) => {
    try {
      const response = await datasetsApi.get(currentProject.id, dataset.id);
      setPreviewData(response.data);
      setSelectedDataset(dataset);
    } catch (error) {
      console.error('Failed to load dataset:', error);
      alert('Failed to load dataset');
    }
  };

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Database size={64} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Project Selected</h2>
          <p className="text-gray-600">Please select or create a project to manage datasets</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dataset Manager</h1>
        <p className="text-gray-600 mt-2">
          View, validate, and export your generated datasets
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading datasets...</p>
        </div>
      ) : datasets.length === 0 ? (
        <div className="text-center py-12 card">
          <Database size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Datasets Yet</h3>
          <p className="text-gray-600 mb-6">
            Generate data first to create datasets
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {datasets.map((dataset) => (
            <div key={dataset.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {dataset.name}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Created {formatDate(dataset.created_at)}
                  </p>
                </div>
                {dataset.validated && (
                  <CheckCircle size={24} className="text-green-600" />
                )}
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-gray-200">
                <div>
                  <div className="text-2xl font-bold text-primary-600">
                    {dataset.sample_count || 0}
                  </div>
                  <div className="text-sm text-gray-600">Samples</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-primary-600">
                    {formatBytes(dataset.size || 0)}
                  </div>
                  <div className="text-sm text-gray-600">Size</div>
                </div>
              </div>

              {dataset.metadata && (
                <div className="mb-4 text-sm">
                  <div className="text-gray-600">
                    Mode: <span className="font-semibold text-gray-900">{dataset.metadata.mode}</span>
                  </div>
                  <div className="text-gray-600">
                    Model: <span className="font-semibold text-gray-900">{dataset.metadata.model}</span>
                  </div>
                </div>
              )}

              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => handlePreviewDataset(dataset)}
                  className="flex-1 btn-secondary text-sm flex items-center justify-center space-x-2"
                >
                  <Eye size={16} />
                  <span>Preview</span>
                </button>
                <button
                  onClick={() => handleValidateDataset(dataset.id)}
                  className="flex-1 btn-secondary text-sm flex items-center justify-center space-x-2"
                >
                  <CheckCircle size={16} />
                  <span>Validate</span>
                </button>
              </div>

              <div className="flex gap-2 mt-2">
                <div className="flex-1 relative group">
                  <button className="w-full btn-primary text-sm flex items-center justify-center space-x-2">
                    <Download size={16} />
                    <span>Export</span>
                  </button>
                  <div className="absolute bottom-full mb-2 left-0 w-full bg-white rounded-lg shadow-lg border border-gray-200 hidden group-hover:block z-10">
                    <button
                      onClick={() => handleExportDataset(dataset.id, 'jsonl')}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100 first:rounded-t-lg"
                    >
                      JSONL
                    </button>
                    <button
                      onClick={() => handleExportDataset(dataset.id, 'csv')}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100"
                    >
                      CSV
                    </button>
                    <button
                      onClick={() => handleExportDataset(dataset.id, 'parquet')}
                      className="block w-full text-left px-4 py-2 hover:bg-gray-100 last:rounded-b-lg"
                    >
                      Parquet
                    </button>
                  </div>
                </div>
                <button
                  onClick={() => handleDeleteDataset(dataset.id)}
                  className="btn-danger text-sm p-2"
                  title="Delete"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Validation Results Modal */}
      {validationResults && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setValidationResults(null)}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">Validation Results</h3>
              <button
                onClick={() => setValidationResults(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>

            <div className="mb-6">
              {validationResults.valid ? (
                <div className="flex items-center space-x-3 text-green-600 bg-green-50 p-4 rounded-lg">
                  <CheckCircle size={24} />
                  <span className="font-semibold">Dataset is valid</span>
                </div>
              ) : (
                <div className="flex items-center space-x-3 text-red-600 bg-red-50 p-4 rounded-lg">
                  <XCircle size={24} />
                  <span className="font-semibold">Dataset has errors</span>
                </div>
              )}
            </div>

            {validationResults.errors && validationResults.errors.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Errors Found:</h4>
                <div className="space-y-2">
                  {validationResults.errors.map((error, idx) => (
                    <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="text-sm font-semibold text-red-900">
                        Sample {error.sample_index}
                      </div>
                      <div className="text-sm text-red-700 mt-1">{error.message}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {validationResults.stats && (
              <div className="mt-6 grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {validationResults.stats.total}
                  </div>
                  <div className="text-sm text-gray-600">Total Samples</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {validationResults.stats.valid}
                  </div>
                  <div className="text-sm text-gray-600">Valid</div>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {validationResults.stats.invalid}
                  </div>
                  <div className="text-sm text-gray-600">Invalid</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {previewData && selectedDataset && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => {
            setPreviewData(null);
            setSelectedDataset(null);
          }}
        >
          <div
            className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">
                {selectedDataset.name} - Preview
              </h3>
              <button
                onClick={() => {
                  setPreviewData(null);
                  setSelectedDataset(null);
                }}
                className="text-gray-500 hover:text-gray-700"
              >
                Close
              </button>
            </div>

            <div className="space-y-4">
              {previewData.samples && previewData.samples.slice(0, 20).map((sample, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="text-sm font-semibold text-gray-700 mb-2">
                    Sample {idx + 1}
                  </div>
                  <pre className="text-sm font-mono text-gray-900 overflow-x-auto">
                    {JSON.stringify(sample, null, 2)}
                  </pre>
                </div>
              ))}
            </div>

            {previewData.samples && previewData.samples.length > 20 && (
              <p className="text-center text-gray-500 mt-4">
                Showing 20 of {previewData.samples.length} samples
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetManager;
