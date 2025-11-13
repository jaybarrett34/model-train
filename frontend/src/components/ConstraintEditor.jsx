import { useState } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import { getConstraintTypeName, validateConstraint } from '../utils/helpers';

const ConstraintEditor = ({ tag, onSave, onClose }) => {
  const [editedTag, setEditedTag] = useState({ ...tag });
  const [activeTab, setActiveTab] = useState('basic');
  const [errors, setErrors] = useState({});

  const constraintTypes = [
    { value: 'regex', label: 'Regular Expression' },
    { value: 'list', label: 'List of Values' },
    { value: 'range', label: 'Numeric Range' },
    { value: 'length', label: 'String Length' },
    { value: 'format', label: 'Format Pattern' },
  ];

  const handleNameChange = (name) => {
    setEditedTag({ ...editedTag, name });
  };

  const handleAddConstraint = (type) => {
    const newConstraints = { ...editedTag.constraints };

    switch (type) {
      case 'regex':
        newConstraints.regex = '';
        break;
      case 'list':
        newConstraints.list = [];
        break;
      case 'range':
        newConstraints.range = { min: 0, max: 100 };
        break;
      case 'length':
        newConstraints.length = { min: 0, max: 100 };
        break;
      case 'format':
        newConstraints.format = '';
        break;
    }

    setEditedTag({ ...editedTag, constraints: newConstraints });
  };

  const handleRemoveConstraint = (type) => {
    const newConstraints = { ...editedTag.constraints };
    delete newConstraints[type];
    setEditedTag({ ...editedTag, constraints: newConstraints });
  };

  const handleConstraintValueChange = (type, value) => {
    const newConstraints = { ...editedTag.constraints };
    newConstraints[type] = value;
    setEditedTag({ ...editedTag, constraints: newConstraints });

    // Validate
    const validation = validateConstraint(type, value);
    if (!validation.valid) {
      setErrors({ ...errors, [type]: validation.error });
    } else {
      const newErrors = { ...errors };
      delete newErrors[type];
      setErrors(newErrors);
    }
  };

  const handleAddAttribute = () => {
    const newAttributes = { ...editedTag.attributes, '': '' };
    setEditedTag({ ...editedTag, attributes: newAttributes });
  };

  const handleAttributeChange = (oldKey, newKey, value) => {
    const newAttributes = { ...editedTag.attributes };
    if (oldKey !== newKey) {
      delete newAttributes[oldKey];
    }
    newAttributes[newKey] = value;
    setEditedTag({ ...editedTag, attributes: newAttributes });
  };

  const handleRemoveAttribute = (key) => {
    const newAttributes = { ...editedTag.attributes };
    delete newAttributes[key];
    setEditedTag({ ...editedTag, attributes: newAttributes });
  };

  const handleSave = () => {
    if (Object.keys(errors).length > 0) {
      alert('Please fix all errors before saving');
      return;
    }
    onSave(editedTag);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900">Configure Tag</h2>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
            <X size={24} />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 px-6">
          <div className="flex space-x-4">
            {['basic', 'constraints', 'attributes'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-3 font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'basic' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tag Name
                </label>
                <input
                  type="text"
                  value={editedTag.name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  className="input-field font-mono"
                  placeholder="e.g., user, product, item"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Must start with a letter or underscore, can contain letters, numbers, hyphens, and periods
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description (optional)
                </label>
                <textarea
                  value={editedTag.description || ''}
                  onChange={(e) => setEditedTag({ ...editedTag, description: e.target.value })}
                  className="input-field"
                  rows="3"
                  placeholder="Describe the purpose of this tag"
                />
              </div>
            </div>
          )}

          {activeTab === 'constraints' && (
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">Constraints</h3>
                  <div className="relative group">
                    <button className="btn-secondary text-sm flex items-center space-x-2">
                      <Plus size={16} />
                      <span>Add Constraint</span>
                    </button>
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 hidden group-hover:block z-10">
                      {constraintTypes.map((type) => (
                        <button
                          key={type.value}
                          onClick={() => handleAddConstraint(type.value)}
                          className="block w-full text-left px-4 py-2 hover:bg-gray-100 first:rounded-t-lg last:rounded-b-lg"
                        >
                          {type.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {Object.keys(editedTag.constraints || {}).length === 0 ? (
                  <p className="text-gray-500 text-center py-8">
                    No constraints defined. Click "Add Constraint" to get started.
                  </p>
                ) : (
                  <div className="space-y-4">
                    {Object.entries(editedTag.constraints).map(([type, value]) => (
                      <div key={type} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <h4 className="font-semibold text-gray-900">
                            {getConstraintTypeName(type)}
                          </h4>
                          <button
                            onClick={() => handleRemoveConstraint(type)}
                            className="p-1 hover:bg-red-100 rounded text-red-600"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>

                        {type === 'regex' && (
                          <div>
                            <input
                              type="text"
                              value={value}
                              onChange={(e) => handleConstraintValueChange(type, e.target.value)}
                              className="input-field font-mono"
                              placeholder="^[A-Za-z]+$"
                            />
                            {errors[type] && (
                              <p className="text-red-600 text-sm mt-1">{errors[type]}</p>
                            )}
                          </div>
                        )}

                        {type === 'list' && (
                          <div>
                            <textarea
                              value={Array.isArray(value) ? value.join('\n') : ''}
                              onChange={(e) => handleConstraintValueChange(type, e.target.value.split('\n').filter(v => v.trim()))}
                              className="input-field font-mono"
                              rows="4"
                              placeholder="Enter one value per line"
                            />
                          </div>
                        )}

                        {(type === 'range' || type === 'length') && (
                          <div className="grid grid-cols-2 gap-4">
                            <div>
                              <label className="block text-sm text-gray-600 mb-1">Min</label>
                              <input
                                type="number"
                                value={value.min}
                                onChange={(e) => handleConstraintValueChange(type, { ...value, min: Number(e.target.value) })}
                                className="input-field"
                              />
                            </div>
                            <div>
                              <label className="block text-sm text-gray-600 mb-1">Max</label>
                              <input
                                type="number"
                                value={value.max}
                                onChange={(e) => handleConstraintValueChange(type, { ...value, max: Number(e.target.value) })}
                                className="input-field"
                              />
                            </div>
                            {errors[type] && (
                              <p className="text-red-600 text-sm col-span-2">{errors[type]}</p>
                            )}
                          </div>
                        )}

                        {type === 'format' && (
                          <div>
                            <select
                              value={value}
                              onChange={(e) => handleConstraintValueChange(type, e.target.value)}
                              className="input-field"
                            >
                              <option value="">Select format...</option>
                              <option value="email">Email</option>
                              <option value="url">URL</option>
                              <option value="uuid">UUID</option>
                              <option value="ipv4">IPv4 Address</option>
                              <option value="date">Date (YYYY-MM-DD)</option>
                              <option value="time">Time (HH:MM:SS)</option>
                            </select>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'attributes' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">XML Attributes</h3>
                <button
                  onClick={handleAddAttribute}
                  className="btn-secondary text-sm flex items-center space-x-2"
                >
                  <Plus size={16} />
                  <span>Add Attribute</span>
                </button>
              </div>

              {Object.keys(editedTag.attributes || {}).length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No attributes defined. Click "Add Attribute" to add XML attributes.
                </p>
              ) : (
                <div className="space-y-3">
                  {Object.entries(editedTag.attributes).map(([key, value]) => (
                    <div key={key} className="flex space-x-3 items-start">
                      <input
                        type="text"
                        value={key}
                        onChange={(e) => handleAttributeChange(key, e.target.value, value)}
                        className="input-field flex-1 font-mono"
                        placeholder="attribute-name"
                      />
                      <input
                        type="text"
                        value={value}
                        onChange={(e) => handleAttributeChange(key, key, e.target.value)}
                        className="input-field flex-1"
                        placeholder="value"
                      />
                      <button
                        onClick={() => handleRemoveAttribute(key)}
                        className="p-2 hover:bg-red-100 rounded text-red-600"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-4">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={Object.keys(errors).length > 0}
            className="btn-primary"
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConstraintEditor;
