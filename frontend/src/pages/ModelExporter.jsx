import { useState, useEffect } from 'react';
import { Download, Package, Trash2, CheckCircle } from 'lucide-react';
import { modelsApi } from '../services/api';
import useStore from '../store/useStore';
import { formatDate, formatBytes } from '../utils/helpers';

const ModelExporter = () => {
  const { currentProject, models, setModels } = useStore();
  const [selectedModel, setSelectedModel] = useState(null);
  const [exportFormat, setExportFormat] = useState('huggingface');
  const [exportOptions, setExportOptions] = useState({
    quantization: 'none',
    includeTokenizer: true,
    includeConfig: true,
    mergeAdapters: true,
  });
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (currentProject) {
      loadModels();
    }
  }, [currentProject]);

  const loadModels = async () => {
    if (!currentProject) return;

    try {
      setLoading(true);
      const response = await modelsApi.list(currentProject.id);
      setModels(response.data);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportModel = async () => {
    if (!selectedModel) {
      alert('Please select a model to export');
      return;
    }

    try {
      setExporting(true);
      const response = await modelsApi.export(currentProject.id, selectedModel.id, {
        format: exportFormat,
        ...exportOptions,
      });

      // Handle download
      if (response.data.downloadUrl) {
        window.open(response.data.downloadUrl, '_blank');
      }

      alert('Export started successfully!');
    } catch (error) {
      console.error('Failed to export model:', error);
      alert('Failed to export model: ' + error.message);
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteModel = async (modelId) => {
    if (!confirm('Are you sure you want to delete this model?')) return;

    try {
      await modelsApi.delete(currentProject.id, modelId);
      setModels(models.filter(m => m.id !== modelId));
      if (selectedModel?.id === modelId) {
        setSelectedModel(null);
      }
    } catch (error) {
      console.error('Failed to delete model:', error);
      alert('Failed to delete model');
    }
  };

  if (!currentProject) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Download size={64} className="mx-auto text-gray-400 mb-4" />
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">No Project Selected</h2>
          <p className="text-gray-600">Please select or create a project to export models</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Model Export</h1>
        <p className="text-gray-600 mt-2">
          Export your trained models in various formats
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading models...</p>
        </div>
      ) : models.length === 0 ? (
        <div className="text-center py-12 card">
          <Package size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Models Yet</h3>
          <p className="text-gray-600 mb-6">
            Train a model first to export it
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Model Selection */}
          <div className="lg:col-span-1">
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Select Model</h2>

              <div className="space-y-3">
                {models.map((model) => (
                  <div
                    key={model.id}
                    onClick={() => setSelectedModel(model)}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedModel?.id === model.id
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-semibold text-gray-900">{model.name}</h3>
                      {selectedModel?.id === model.id && (
                        <CheckCircle size={20} className="text-primary-600" />
                      )}
                    </div>

                    <div className="text-sm text-gray-600 space-y-1">
                      <div>Base: {model.base_model}</div>
                      <div>{formatDate(model.created_at)}</div>
                      {model.size && <div>Size: {formatBytes(model.size)}</div>}
                    </div>

                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteModel(model.id);
                        }}
                        className="text-red-600 hover:text-red-700 text-sm flex items-center space-x-1"
                      >
                        <Trash2 size={14} />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Export Configuration */}
          <div className="lg:col-span-2 space-y-6">
            {selectedModel ? (
              <>
                {/* Model Info */}
                <div className="card">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Model Information</h2>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Model Name</div>
                      <div className="font-semibold text-gray-900">{selectedModel.name}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Base Model</div>
                      <div className="font-semibold text-gray-900">{selectedModel.base_model}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Created</div>
                      <div className="font-semibold text-gray-900">{formatDate(selectedModel.created_at)}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Size</div>
                      <div className="font-semibold text-gray-900">
                        {selectedModel.size ? formatBytes(selectedModel.size) : 'N/A'}
                      </div>
                    </div>
                  </div>

                  {selectedModel.metadata && (
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="text-sm text-gray-600 mb-2">Training Configuration</div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>LoRA Rank: {selectedModel.metadata.lora_r}</div>
                        <div>LoRA Alpha: {selectedModel.metadata.lora_alpha}</div>
                        <div>Learning Rate: {selectedModel.metadata.learning_rate}</div>
                        <div>Epochs: {selectedModel.metadata.epochs}</div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Export Format */}
                <div className="card">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Format</h2>

                  <div className="grid grid-cols-2 gap-4">
                    <button
                      onClick={() => setExportFormat('huggingface')}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        exportFormat === 'huggingface'
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900 mb-1">HuggingFace</div>
                      <div className="text-sm text-gray-600">
                        Standard HF format with adapters
                      </div>
                    </button>

                    <button
                      onClick={() => setExportFormat('gguf')}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        exportFormat === 'gguf'
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900 mb-1">GGUF</div>
                      <div className="text-sm text-gray-600">
                        For llama.cpp inference
                      </div>
                    </button>

                    <button
                      onClick={() => setExportFormat('onnx')}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        exportFormat === 'onnx'
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900 mb-1">ONNX</div>
                      <div className="text-sm text-gray-600">
                        Cross-platform inference
                      </div>
                    </button>

                    <button
                      onClick={() => setExportFormat('safetensors')}
                      className={`p-4 border-2 rounded-lg text-left transition-all ${
                        exportFormat === 'safetensors'
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-semibold text-gray-900 mb-1">SafeTensors</div>
                      <div className="text-sm text-gray-600">
                        Safe model serialization
                      </div>
                    </button>
                  </div>
                </div>

                {/* Export Options */}
                <div className="card">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Export Options</h2>

                  <div className="space-y-4">
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={exportOptions.mergeAdapters}
                        onChange={(e) => setExportOptions({
                          ...exportOptions,
                          mergeAdapters: e.target.checked
                        })}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Merge LoRA Adapters</div>
                        <div className="text-sm text-gray-600">
                          Merge adapters into base model for faster inference
                        </div>
                      </div>
                    </label>

                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={exportOptions.includeTokenizer}
                        onChange={(e) => setExportOptions({
                          ...exportOptions,
                          includeTokenizer: e.target.checked
                        })}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Include Tokenizer</div>
                        <div className="text-sm text-gray-600">
                          Include tokenizer files in export
                        </div>
                      </div>
                    </label>

                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={exportOptions.includeConfig}
                        onChange={(e) => setExportOptions({
                          ...exportOptions,
                          includeConfig: e.target.checked
                        })}
                        className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
                      />
                      <div>
                        <div className="font-medium text-gray-900">Include Config Files</div>
                        <div className="text-sm text-gray-600">
                          Include model configuration and metadata
                        </div>
                      </div>
                    </label>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Quantization
                      </label>
                      <select
                        value={exportOptions.quantization}
                        onChange={(e) => setExportOptions({
                          ...exportOptions,
                          quantization: e.target.value
                        })}
                        className="input-field"
                      >
                        <option value="none">None - Full Precision</option>
                        <option value="int8">INT8 - 8-bit quantization</option>
                        <option value="int4">INT4 - 4-bit quantization</option>
                        <option value="nf4">NF4 - 4-bit NormalFloat</option>
                        <option value="fp16">FP16 - Half precision</option>
                      </select>
                      <p className="text-sm text-gray-500 mt-1">
                        Quantization reduces model size but may affect quality
                      </p>
                    </div>
                  </div>
                </div>

                {/* Export Button */}
                <div className="card bg-primary-50 border-2 border-primary-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-1">Ready to Export</h3>
                      <p className="text-sm text-gray-600">
                        Format: {exportFormat.toUpperCase()}
                        {exportOptions.quantization !== 'none' && ` with ${exportOptions.quantization.toUpperCase()} quantization`}
                      </p>
                    </div>
                    <button
                      onClick={handleExportModel}
                      disabled={exporting}
                      className="btn-primary flex items-center space-x-2"
                    >
                      <Download size={20} />
                      <span>{exporting ? 'Exporting...' : 'Export Model'}</span>
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="card text-center py-12">
                <Package size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-600">Select a model from the left to configure export</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelExporter;
