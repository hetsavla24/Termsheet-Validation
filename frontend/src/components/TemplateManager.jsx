import React, { useState, useEffect } from 'react';
import { validationAPI } from '../api';

const TemplateManager = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    template_name: '',
    description: '',
    validation_rules: []
  });

  const [newRule, setNewRule] = useState({
    term_name: '',
    expected_value: '',
    expected_range: '',
    validation_type: 'exact_match',
    required: true,
    tolerance: 0.8
  });

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await validationAPI.getTemplates();
      setTemplates(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTemplate = async (e) => {
    e.preventDefault();
    try {
      if (formData.validation_rules.length === 0) {
        setError('Please add at least one validation rule');
        return;
      }

      await validationAPI.createTemplate(formData);
      setShowCreateForm(false);
      setFormData({
        template_name: '',
        description: '',
        validation_rules: []
      });
      loadTemplates();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create template');
    }
  };

  const addRule = () => {
    if (!newRule.term_name.trim()) {
      setError('Term name is required');
      return;
    }

    if (newRule.validation_type !== 'range_check' && !newRule.expected_value.trim()) {
      setError('Expected value is required for this validation type');
      return;
    }

    if (newRule.validation_type === 'range_check' && !newRule.expected_range.trim()) {
      setError('Expected range is required for range validation');
      return;
    }

    setFormData(prev => ({
      ...prev,
      validation_rules: [...prev.validation_rules, { ...newRule }]
    }));

    setNewRule({
      term_name: '',
      expected_value: '',
      expected_range: '',
      validation_type: 'exact_match',
      required: true,
      tolerance: 0.8
    });
    setError(null);
  };

  const removeRule = (index) => {
    setFormData(prev => ({
      ...prev,
      validation_rules: prev.validation_rules.filter((_, i) => i !== index)
    }));
  };

  const getValidationTypeColor = (type) => {
    const colors = {
      'exact_match': 'bg-blue-100 text-blue-800',
      'fuzzy_match': 'bg-green-100 text-green-800',
      'range_check': 'bg-purple-100 text-purple-800',
      'pattern_match': 'bg-orange-100 text-orange-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Validation Templates</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Create Template
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Template List */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {templates.map((template) => (
          <div key={template.id} className="bg-white rounded-lg shadow-md p-6 border">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {template.template_name}
            </h3>
            {template.description && (
              <p className="text-gray-600 mb-4">{template.description}</p>
            )}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Rules:</span>
                <span className="font-medium">
                  {JSON.parse(template.validation_rules).length}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Created:</span>
                <span className="text-gray-900">
                  {new Date(template.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Status:</span>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  template.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {template.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {templates.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-2">No templates found</div>
          <p className="text-gray-500">Create your first validation template to get started</p>
        </div>
      )}

      {/* Create Template Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Create Validation Template</h3>
            
            <form onSubmit={handleCreateTemplate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template Name*
                </label>
                <input
                  type="text"
                  value={formData.template_name}
                  onChange={(e) => setFormData(prev => ({...prev, template_name: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({...prev, description: e.target.value}))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows="3"
                />
              </div>

              {/* Add Rule Section */}
              <div className="border-t pt-4">
                <h4 className="text-lg font-semibold mb-3">Add Validation Rule</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Term Name*
                    </label>
                    <select
                      value={newRule.term_name}
                      onChange={(e) => setNewRule(prev => ({...prev, term_name: e.target.value}))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="">Select term type</option>
                      <option value="valuation">Valuation</option>
                      <option value="investment_amount">Investment Amount</option>
                      <option value="equity_percentage">Equity Percentage</option>
                      <option value="liquidation_preference">Liquidation Preference</option>
                      <option value="anti_dilution">Anti-Dilution</option>
                      <option value="board_seats">Board Seats</option>
                      <option value="dividend_rate">Dividend Rate</option>
                      <option value="company_name">Company Name</option>
                      <option value="investor_name">Investor Name</option>
                      <option value="date_field">Date Field</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Validation Type*
                    </label>
                    <select
                      value={newRule.validation_type}
                      onChange={(e) => setNewRule(prev => ({...prev, validation_type: e.target.value}))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    >
                      <option value="exact_match">Exact Match</option>
                      <option value="fuzzy_match">Fuzzy Match</option>
                      <option value="range_check">Range Check</option>
                      <option value="pattern_match">Pattern Match</option>
                    </select>
                  </div>

                  {newRule.validation_type !== 'range_check' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Expected Value*
                      </label>
                      <input
                        type="text"
                        value={newRule.expected_value}
                        onChange={(e) => setNewRule(prev => ({...prev, expected_value: e.target.value}))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        placeholder="e.g., $5 million, 20%, weighted average"
                      />
                    </div>
                  )}

                  {newRule.validation_type === 'range_check' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Expected Range*
                      </label>
                      <input
                        type="text"
                        value={newRule.expected_range}
                        onChange={(e) => setNewRule(prev => ({...prev, expected_range: e.target.value}))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        placeholder="e.g., 1-10, >=5, <100"
                      />
                    </div>
                  )}

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="required"
                      checked={newRule.required}
                      onChange={(e) => setNewRule(prev => ({...prev, required: e.target.checked}))}
                      className="mr-2"
                    />
                    <label htmlFor="required" className="text-sm text-gray-700">
                      Required Field
                    </label>
                  </div>

                  {newRule.validation_type === 'fuzzy_match' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Tolerance (0.0 - 1.0)
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="1"
                        step="0.1"
                        value={newRule.tolerance}
                        onChange={(e) => setNewRule(prev => ({...prev, tolerance: parseFloat(e.target.value)}))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                      />
                    </div>
                  )}
                </div>

                <button
                  type="button"
                  onClick={addRule}
                  className="mt-3 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Add Rule
                </button>
              </div>

              {/* Current Rules */}
              {formData.validation_rules.length > 0 && (
                <div className="border-t pt-4">
                  <h4 className="text-lg font-semibold mb-3">Validation Rules ({formData.validation_rules.length})</h4>
                  <div className="space-y-2">
                    {formData.validation_rules.map((rule, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 p-3 rounded-md">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium">{rule.term_name}</span>
                            <span className={`px-2 py-1 rounded-full text-xs ${getValidationTypeColor(rule.validation_type)}`}>
                              {rule.validation_type}
                            </span>
                            {rule.required && (
                              <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs">
                                Required
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-600">
                            {rule.validation_type === 'range_check' 
                              ? `Range: ${rule.expected_range}`
                              : `Expected: ${rule.expected_value}`
                            }
                            {rule.validation_type === 'fuzzy_match' && ` (tolerance: ${rule.tolerance})`}
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeRule(index)}
                          className="text-red-500 hover:text-red-700 p-1"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                >
                  Create Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default TemplateManager; 