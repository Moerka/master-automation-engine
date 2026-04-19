# Unified Workflow Integration Guide

Complete guide for integrating all Manus skills into cohesive automation workflows.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Workflow Orchestrator                     │
│  (Triggers, Conditions, Actions, Error Handling)           │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
┌───▼────┐  ┌────────▼────┐  ┌─────▼──────┐  ┌────▼─────┐
│  GWS   │  │   Excel     │  │   Video    │  │   BGM    │
│Workflow│  │ Generator   │  │ Generator  │  │ Prompter │
└────────┘  └─────────────┘  └────────────┘  └──────────┘

    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
┌───▼────┐  ┌────────▼────┐  ┌─────▼──────┐  ┌────▼─────┐
│ GitHub │  │  Internet   │  │ SimilarWeb │  │Credential│
│  Gem   │  │  Skill      │  │ Analytics  │  │ Manager  │
│ Seeker │  │  Finder     │  │            │  │          │
└────────┘  └─────────────┘  └────────────┘  └──────────┘
```

## Workflow Types

### 1. E-Commerce Setup Workflow

**Goal**: Create a fully functional e-commerce store in 5 minutes

```yaml
workflow:
  name: "Quick E-Store Setup"
  mastery: "beginner"
  steps:
    - step: "template_selection"
      action: "select_template"
      templates: ["shopify-like", "etsy-like", "b2b"]
      
    - step: "basic_config"
      action: "configure_store"
      fields:
        - store_name
        - currency
        - timezone
        
    - step: "payment_setup"
      action: "setup_payment"
      services: ["stripe", "paypal", "square"]
      requires: "credential_manager"
      
    - step: "product_import"
      action: "import_products"
      formats: ["csv", "json", "manual"]
      
    - step: "deploy"
      action: "deploy_store"
      domain: "auto-generated"
      ssl: "auto"
      
    - step: "verification"
      action: "verify_setup"
      checks:
        - payment_processing
        - product_display
        - checkout_flow
```

### 2. Content Generation Workflow

**Goal**: Auto-generate product content (descriptions, images, videos, audio)

```yaml
workflow:
  name: "Product Content Generation"
  mastery: "developer"
  trigger: "product_created"
  
  steps:
    - step: "extract_product_data"
      action: "read_from_store"
      fields: ["name", "category", "price", "image"]
      
    - step: "generate_description"
      action: "openai_api"
      prompt: "Generate compelling product description"
      requires: "credential_manager"
      
    - step: "generate_marketing_copy"
      action: "bgm_prompter"
      style: "persuasive"
      
    - step: "generate_demo_video"
      action: "video_generator"
      duration: "30-60 seconds"
      requires: "video_generation_credits"
      
    - step: "generate_background_music"
      action: "bgm_prompter"
      mood: "uplifting"
      duration: "match_video"
      
    - step: "create_excel_report"
      action: "excel_generator"
      template: "product_performance"
      
    - step: "publish_content"
      action: "update_store"
      content: ["description", "copy", "video", "audio"]
```

### 3. Competitive Analysis Workflow

**Goal**: Analyze competitors and generate intelligence report

```yaml
workflow:
  name: "Competitive Intelligence"
  mastery: "expert"
  schedule: "weekly"
  
  steps:
    - step: "identify_competitors"
      action: "manual_input"
      fields: ["competitor_domains"]
      
    - step: "fetch_similarweb_data"
      action: "similarweb_analytics"
      metrics:
        - global_rank
        - monthly_visits
        - traffic_sources
        - geographic_distribution
        - engagement_metrics
      requires: "credential_manager"
      
    - step: "analyze_trends"
      action: "data_analysis"
      compare: "our_store vs competitors"
      
    - step: "generate_excel_report"
      action: "excel_generator"
      template: "competitive_analysis"
      include:
        - rankings_chart
        - traffic_comparison
        - market_share
        - recommendations
        
    - step: "create_presentation"
      action: "gws_slides"
      template: "executive_summary"
      
    - step: "send_report"
      action: "gws_docs"
      recipients: ["stakeholders"]
      format: "pdf"
```

### 4. Marketing Campaign Workflow

**Goal**: Execute end-to-end marketing campaign

```yaml
workflow:
  name: "Marketing Campaign"
  mastery: "expert"
  
  steps:
    - step: "campaign_planning"
      action: "competitive_analysis"
      using: "similarweb_analytics"
      
    - step: "content_creation"
      actions:
        - generate_product_images: "video_generator"
        - generate_copy: "bgm_prompter"
        - generate_videos: "video_generator"
        - generate_music: "bgm_prompter"
        
    - step: "email_campaign"
      action: "mailchimp_integration"
      requires: "credential_manager"
      segments:
        - new_customers
        - repeat_buyers
        - inactive_users
        
    - step: "social_media"
      action: "slack_integration"
      schedule: "posts"
      
    - step: "analytics"
      action: "google_analytics"
      track:
        - click_through_rate
        - conversion_rate
        - revenue_per_campaign
        
    - step: "reporting"
      action: "excel_generator"
      template: "campaign_performance"
      
    - step: "optimization"
      action: "ai_recommendations"
      based_on: "performance_data"
```

## Skill Integration Patterns

### Pattern 1: Sequential Integration

```typescript
// Execute skills in sequence
const workflow = new Workflow({
  steps: [
    { skill: 'similarweb', action: 'analyze' },
    { skill: 'excel-generator', action: 'create_report' },
    { skill: 'gws', action: 'upload_to_sheets' },
    { skill: 'mailchimp', action: 'send_email' }
  ]
});

await workflow.execute();
```

### Pattern 2: Parallel Integration

```typescript
// Execute skills in parallel
const workflow = new Workflow({
  parallel: [
    { skill: 'video-generator', action: 'create_video' },
    { skill: 'bgm-prompter', action: 'create_music' },
    { skill: 'excel-generator', action: 'create_report' }
  ]
});

await workflow.execute();
```

### Pattern 3: Conditional Integration

```typescript
// Execute skills based on conditions
const workflow = new Workflow({
  steps: [
    {
      skill: 'similarweb',
      action: 'analyze',
      if: 'competitor_traffic > threshold'
    },
    {
      skill: 'video-generator',
      action: 'create_response_video',
      if: 'competitor_launched_new_product'
    }
  ]
});

await workflow.execute();
```

### Pattern 4: Error Handling Integration

```typescript
// Handle errors and retry
const workflow = new Workflow({
  steps: [
    {
      skill: 'video-generator',
      action: 'create_video',
      retry: {
        maxAttempts: 3,
        backoff: 'exponential'
      },
      onError: {
        fallback: 'use_template_video',
        notify: 'admin'
      }
    }
  ]
});

await workflow.execute();
```

## Real-World Workflow Examples

### Example 1: Auto-Generated E-Store with Content

```typescript
const autoStore = new MasterWorkflow({
  name: 'Auto-Generated E-Store',
  
  async execute() {
    // 1. Create store
    const store = await webdev.createStore({
      template: 'shopify-like',
      name: 'My Store'
    });
    
    // 2. Setup payment
    const stripe = await credentialManager.get('stripe.secret_key');
    await store.setupPayment(stripe);
    
    // 3. Import products
    const products = await csv.import('products.csv');
    
    // 4. Generate content for each product
    for (const product of products) {
      // Generate description
      const description = await openai.generate(
        `Create product description for ${product.name}`
      );
      
      // Generate video
      const video = await videoGenerator.create({
        product: product.name,
        duration: '30s'
      });
      
      // Generate music
      const music = await bgmPrompter.create({
        mood: 'uplifting',
        duration: '30s'
      });
      
      // Update product
      await store.updateProduct(product.id, {
        description,
        video,
        music
      });
    }
    
    // 5. Deploy
    await store.deploy({
      domain: 'auto-generated',
      ssl: true
    });
    
    return store;
  }
});
```

### Example 2: Competitive Intelligence Dashboard

```typescript
const competitiveIntelligence = new MasterWorkflow({
  name: 'Competitive Intelligence',
  schedule: 'weekly',
  
  async execute() {
    // 1. Analyze competitors
    const competitors = ['competitor1.com', 'competitor2.com'];
    const analysis = await Promise.all(
      competitors.map(domain =>
        similarweb.analyze(domain)
      )
    );
    
    // 2. Create Excel report
    const report = await excelGenerator.create({
      template: 'competitive_analysis',
      data: analysis
    });
    
    // 3. Create presentation
    const presentation = await gwsSlides.create({
      template: 'executive_summary',
      data: analysis
    });
    
    // 4. Send to stakeholders
    await mailchimp.sendEmail({
      recipients: ['stakeholders@company.com'],
      subject: 'Weekly Competitive Analysis',
      attachments: [report, presentation]
    });
    
    return { report, presentation };
  }
});
```

## Workflow State Management

```typescript
interface WorkflowState {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  steps: StepState[];
  errors: Error[];
  results: Record<string, any>;
}

interface StepState {
  id: string;
  skill: string;
  action: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  duration: number;
  result?: any;
  error?: Error;
}
```

## Monitoring & Debugging

```typescript
// Monitor workflow execution
const monitor = new WorkflowMonitor({
  onStepStart: (step) => console.log(`Starting ${step.id}`),
  onStepComplete: (step) => console.log(`Completed ${step.id}`),
  onStepError: (step, error) => console.error(`Failed ${step.id}:`, error),
  onWorkflowComplete: (workflow) => console.log(`Workflow done: ${workflow.name}`)
});

// Debug workflow
const debug = await workflow.debug({
  verbose: true,
  captureState: true,
  logToFile: 'workflow-debug.log'
});
```
