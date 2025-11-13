/**
 * Generate a unique ID
 */
export const generateId = () => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Format bytes to human readable string
 */
export const formatBytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Format date to human readable string
 */
export const formatDate = (date) => {
  return new Date(date).toLocaleString();
};

/**
 * Validate XML tag name
 */
export const isValidTagName = (name) => {
  const regex = /^[a-zA-Z_][\w.-]*$/;
  return regex.test(name);
};

/**
 * Convert XML pattern to string
 */
export const patternToXml = (tags, rootTagId) => {
  const buildXmlNode = (tagId, indent = 0) => {
    const tag = tags.find(t => t.id === tagId);
    if (!tag) return '';

    const indentStr = '  '.repeat(indent);
    const attrs = tag.attributes ? ` ${Object.entries(tag.attributes).map(([k, v]) => `${k}="${v}"`).join(' ')}` : '';

    if (tag.children && tag.children.length > 0) {
      const childrenXml = tag.children.map(childId => buildXmlNode(childId, indent + 1)).join('\n');
      return `${indentStr}<${tag.name}${attrs}>\n${childrenXml}\n${indentStr}</${tag.name}>`;
    } else {
      return `${indentStr}<${tag.name}${attrs} />`;
    }
  };

  return buildXmlNode(rootTagId);
};

/**
 * Clone deep object
 */
export const cloneDeep = (obj) => {
  return JSON.parse(JSON.stringify(obj));
};

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Get constraint type display name
 */
export const getConstraintTypeName = (type) => {
  const names = {
    regex: 'Regular Expression',
    list: 'List of Values',
    range: 'Numeric Range',
    length: 'String Length',
    format: 'Format Pattern',
    custom: 'Custom Constraint',
  };
  return names[type] || type;
};

/**
 * Validate constraint value
 */
export const validateConstraint = (type, value) => {
  switch (type) {
    case 'regex':
      try {
        new RegExp(value);
        return { valid: true };
      } catch (e) {
        return { valid: false, error: 'Invalid regular expression' };
      }
    case 'range':
      if (value.min !== undefined && value.max !== undefined && value.min > value.max) {
        return { valid: false, error: 'Min value must be less than max value' };
      }
      return { valid: true };
    case 'list':
      if (!Array.isArray(value) || value.length === 0) {
        return { valid: false, error: 'List must contain at least one value' };
      }
      return { valid: true };
    default:
      return { valid: true };
  }
};
