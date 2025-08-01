// Your Plugin Template for Claude Code UI
// This serves as a template demonstrating all major plugin capabilities

class YourPlugin {
  constructor(api) {
    this.api = api;
    this.isInitialized = false;
    
    // Initialize your plugin state here
    this.customState = {};
  }

  async init() {
    try {
      this.api.log.info('Initializing Your Plugin');
      
      // Register chat tools
      await this.registerChatTools();
      
      // Register keyboard shortcuts
      await this.registerKeyboardShortcuts();
      
      // Register quick settings
      await this.registerQuickSettings();
      
      // Set up message listeners
      this.setupMessageListeners();
      
      // Register custom message types
      await this.registerCustomMessages();
      
      this.isInitialized = true;
      this.api.log.info('Your Plugin initialized successfully');
      
      return this;
    } catch (error) {
      this.api.log.error('Failed to initialize Your Plugin:', error);
      throw error;
    }
  }

  async registerChatTools() {
    // Example chat tool - replace with your own
    const exampleTool = {
      id: 'your-plugin-example-tool',
      name: 'your_plugin_action',
      description: 'Describe what your tool does here',
      parameters: {
        type: 'object',
        properties: {
          input: {
            type: 'string',
            description: 'Input parameter description'
          },
          option: {
            type: 'string',
            enum: ['option1', 'option2', 'option3'],
            description: 'Option parameter description'
          }
        },
        required: ['input']
      },
      handler: this.handleExampleTool.bind(this)
    };

    await this.api.chat.addTool(exampleTool);
    this.api.log.info('Registered your_plugin_action chat tool');
  }

  async handleExampleTool(params) {
    const settings = await this.api.settings.get('');
    const enableFeature = settings.enableFeature !== false;
    
    if (!enableFeature) {
      return {
        success: false,
        message: 'Feature is disabled in settings'
      };
    }

    // TODO: Implement your tool logic here
    const result = `Processing: ${params.input} with option: ${params.option || 'default'}`;

    // Send custom message if needed
    await this.api.messages.sendCustomMessage({
      type: 'your-plugin-result',
      content: result,
      metadata: {
        input: params.input,
        option: params.option,
        timestamp: new Date().toISOString()
      }
    });

    return {
      success: true,
      message: result
    };
  }

  async registerKeyboardShortcuts() {
    // Example keyboard shortcut - replace with your own
    await this.api.keyboard.addShortcut({
      id: 'your-plugin-shortcut',
      key: 'ctrl+shift+y', // Change to your preferred shortcut
      description: 'Trigger your plugin action',
      handler: async () => {
        await this.handleExampleTool({ input: 'shortcut trigger' });
      }
    });

    this.api.log.info('Registered keyboard shortcuts');
  }

  async registerQuickSettings() {
    // Example quick toggle - replace with your own
    await this.api.quickSettings.add({
      id: 'your-plugin-toggle',
      label: 'Enable Feature',
      type: 'toggle',
      value: await this.api.settings.get('enableFeature') !== false,
      onChange: async (value) => {
        await this.api.settings.set('enableFeature', value);
      }
    });

    // Example quick display - replace with your own
    await this.api.quickSettings.add({
      id: 'your-plugin-display',
      label: 'Status',
      type: 'display',
      value: () => this.isInitialized ? 'Active' : 'Inactive',
      onClick: () => {
        this.api.log.info('Status clicked');
      }
    });

    this.api.log.info('Registered quick settings');
  }

  setupMessageListeners() {
    // Listen for settings changes
    this.api.settings.onChange((key, value) => {
      this.api.log.info(`Setting changed: ${key} = ${value}`);
      
      // Update quick settings if needed
      if (key === 'enableFeature') {
        this.api.quickSettings.update('your-plugin-toggle', value);
      }
    });

    // Listen for chat messages
    this.api.chat.onMessage((message) => {
      // TODO: Implement your message handling logic
      // Example: Auto-respond to certain messages
      if (message.content && message.content.toLowerCase().includes('trigger plugin')) {
        this.handleExampleTool({ input: 'message trigger' });
      }
    });

    this.api.log.info('Set up message listeners');
  }

  async registerCustomMessages() {
    // Register custom message type for your plugin
    await this.api.messages.addCustomType({
      type: 'your-plugin-result',
      name: 'Your Plugin Result',
      icon: '⚡', // Change to your preferred icon
      render: (message) => ({
        type: 'component',
        component: 'YourPluginMessage',
        props: {
          content: message.content,
          metadata: message.metadata
        }
      })
    });

    this.api.log.info('Registered custom message types');
  }

  // Plugin lifecycle methods
  async onEnable() {
    this.api.log.info('Your Plugin enabled');
    if (!this.isInitialized) {
      await this.init();
    }
  }

  async onDisable() {
    this.api.log.info('Your Plugin disabled');
    
    // Clean up resources
    await this.api.chat.removeTool('your-plugin-example-tool');
    await this.api.keyboard.removeShortcut('your-plugin-shortcut');
    await this.api.quickSettings.remove('your-plugin-toggle');
    await this.api.quickSettings.remove('your-plugin-display');
  }

  async cleanup() {
    await this.onDisable();
    this.api.log.info('Your Plugin cleaned up');
  }

  // Plugin API methods
  getInfo() {
    return {
      name: 'Your Plugin Name',
      version: '1.0.0',
      author: 'Your Name',
      description: 'A brief description of what your plugin does',
      isInitialized: this.isInitialized
    };
  }

  async getStats() {
    return {
      isInitialized: this.isInitialized,
      currentSettings: await this.api.settings.get('')
    };
  }

  // Add your custom methods here
  customMethod() {
    // TODO: Implement your custom functionality
    return 'Custom method result';
  }
}

// React component for custom messages
const YourPluginMessage = ({ content, metadata }) => {
  return (
    <div className="your-plugin-message bg-green-50 border-l-4 border-green-400 p-4 my-2">
      <div className="flex items-center">
        <span className="text-2xl mr-2">⚡</span>
        <div className="flex-1">
          <p className="text-green-800 font-medium">{content}</p>
          {metadata && (
            <div className="text-xs text-green-600 mt-1">
              Input: {metadata.input}
              {metadata.option && ` • Option: ${metadata.option}`}
              {metadata.timestamp && ` • ${new Date(metadata.timestamp).toLocaleTimeString()}`}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Plugin exports
module.exports = {
  // Main plugin class
  init: (api) => {
    const plugin = new YourPlugin(api);
    return plugin.init();
  },
  
  // Plugin metadata
  getModule: () => ({
    YourPlugin,
    init: (api) => new YourPlugin(api).init(),
    cleanup: (plugin) => plugin.cleanup()
  }),

  // React components
  components: {
    YourPluginMessage
  },

  // Plugin actions for external calls
  actions: {
    customAction: (plugin, params) => plugin.customMethod(params),
    getStats: (plugin) => plugin.getStats()
  }
};