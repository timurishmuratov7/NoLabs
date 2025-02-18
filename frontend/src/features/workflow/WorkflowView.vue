<template>
  <q-page class="bg-black">
    <BioBuddyChat v-if="bioBuddyEnabled" :experiment-id="experiment.experimentId as string" />
    <div class="row no-wrap items-center">
      <q-btn-dropdown color="primary" label="Add Node" icon="add" dense persistent>
        <q-list>
          <q-item v-for="option in componentOptions" :key="option.name" clickable v-close-popup
            @click="addComponent(option)">
            <q-item-section>
              <q-item-label>{{ option.name }}</q-item-label>
              <q-item-label caption>{{ option.description }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-btn-dropdown>
      <q-space />
      <q-btn v-if="!isWorkflowRunning && !isLocallyRunning" class="q-ma-sm" color="info" icon="not_started"
        @click="startWorkflow">
        Start workflow
      </q-btn>
      <q-btn v-else :disable="true" class="q-ma-sm" color="info" icon="running">
        <q-spinner color="white" size="20px" />
        Running...
      </q-btn>
    </div>

    <div class="map-container">
      <VueFlow class="workflow" scale="0.5" v-if="elements" :nodes="elements.nodes"
        @nodeDragStop="onNodeDragStopHandler" :removeEdge="onEdgeUpdate" @connect="onConnect" :edges="elements.edges"
        fit-view-on-init>
        <template #node-Proteins="{ id }">
          <ProteinListNode :nodeId="id" :onDeleteNode="onDeleteNode" :onOpenSettings="openSettings"
            :onOpenDialog="openNodeDialog" />
        </template>
        <template #node-Ligands="{ id }">
          <LigandListNode :nodeId="id" :onDeleteNode="onDeleteNode" :onOpenSettings="openSettings"
            :onOpenDialog="openNodeDialog" />
        </template>
        <template #node-custom="{ id }">
          <JobNode :nodeId="id" :onDeleteNode="onDeleteNode" :onOpenSettings="openSettings"
            :onOpenDialog="openNodeDialog" />
        </template>
        <template #edge-custom="customEdgeProps">
          <ErrorEdge :id="customEdgeProps.id" :source-x="customEdgeProps.sourceX" :source-y="customEdgeProps.sourceY"
            :target-x="customEdgeProps.targetX" :target-y="customEdgeProps.targetY"
            :source-position="customEdgeProps.sourcePosition" :target-position="customEdgeProps.targetPosition"
            :data="customEdgeProps.data" :marker-end="customEdgeProps.markerEnd" :style="customEdgeProps.style" />
        </template>
      </VueFlow>
    </div>

    <q-dialog v-model="modalOpen" persistent>
      <q-card style="min-width: 70vw; min-height: 70vh;">
        <q-card-actions align="right">
          <q-btn flat round dense icon="close" v-close-popup @click="closeModal" />
        </q-card-actions>
        <q-card-section>
          <ProteinListNodeContent v-if="experiment.experimentId && selectedNode && selectedNode.type === 'Proteins'"
            :experiment-id="experiment.experimentId" :nodeId="selectedNode.id" />
          <LigandListNodeContent v-if="experiment.experimentId && selectedNode && selectedNode.type === 'Ligands'"
            :experiment-id="experiment.experimentId" :nodeId="selectedNode.id" />
          <JobNodeContent v-if="experiment.experimentId && selectedNode && selectedNode.type === 'custom'"
            :nodeId="selectedNode?.id" :name="selectedNode?.name" :description="selectedNode?.description ?? ''" />
        </q-card-section>
      </q-card>
    </q-dialog>
  </q-page>
</template>


<script lang="ts">
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';

import { io } from 'socket.io-client';

import BioBuddyChat from "src/features/biobuddy/BioBuddyChat.vue";
import ProteinListNode from "./components/nodeTemplates/dataSourceNodes/proteins/ProteinListNode.vue";
import ProteinListNodeContent from "./components/nodeTemplates/dataSourceNodes/proteins/ProteinListNodeContent.vue";
import LigandListNode from "./components/nodeTemplates/dataSourceNodes/ligands/LigandListNode.vue";
import LigandListNodeContent from "./components/nodeTemplates/dataSourceNodes/ligands/LigandListNodeContent.vue";
import ErrorEdge from "./components/nodeTemplates/ErrorEdge.vue"
import { defineComponent, onBeforeUnmount } from "vue";
import { VueFlow } from '@vue-flow/core';
import JobNode from "./components/nodeTemplates/JobNode.vue";
import JobNodeContent from "./components/nodeTemplates/JobNodeContent.vue";
import {
  startWorkflow,
  checkBiobuddyEnabled,
  createWorkflow,
  getWorkflow,
  getComponentState,
} from './refinedApi';
import { useWorkflowStore, Edge, Node } from './components/storage';
import { useBioBuddyStore } from "src/features/biobuddy/storage";
import {ComponentStateEnum, JobStateEnum} from "../../refinedApi/client";

export default defineComponent({
  name: "WorkflowView",
  components: {
    BioBuddyChat,
    VueFlow,
    ProteinListNode,
    ProteinListNodeContent,
    LigandListNode,
    LigandListNodeContent,
    JobNode,
    JobNodeContent,
    ErrorEdge
  },
  data() {
    return {
      step: 1, // This can be a reactive property based on the current route if needed
      experiment: {
        experimentId: null as string | null,
        metadata: null
      },
      elements: {
        nodes: [] as Node[],
        edges: [] as Edge[]
      },
      allowedTypes: ["Proteins", "Ligands", "DNA"],
      sideMenuOpen: false,
      modalOpen: false,
      selectedNode: null as Node | null,
      selectedComponent: null as string | null,
      socket: null as WebSocket | null,
      specialNodeProps: [],
      splitterModel: 20,
      bioBuddyEnabled: false,
      biobuddyWorkflowCallBack: null as ((data: any) => void) | null,
      pollIntervalId: null as number | null, // Interval ID for polling
      isLocallyRunning: false // Local running state
    };
  },
  computed: {
    componentOptions() {
      const workflowStore = useWorkflowStore();
      return workflowStore.componentOptions;
    },
    isWorkflowRunning() {
      const workflowStore = useWorkflowStore();
      return workflowStore.workflowIsRunning;
    }
  },
  watch: {
    isWorkflowRunning(newVal) {
      if (newVal !== this.isLocallyRunning) {
        this.isLocallyRunning = newVal;
      }
    }
  },
  async mounted() {
    this.experiment.experimentId = this.$route.params.experimentId as string;

    try {
      this.bioBuddyEnabled = await checkBiobuddyEnabled();
    } catch (error) {
      console.error('Error checking BioBuddy enabled status:', error);
      this.bioBuddyEnabled = false;
    }

    // Check if workflow exists, if not, create one
    await this.checkAndCreateWorkflow();

    const workflowStore = useWorkflowStore();
    await workflowStore.getAllProteins(this.experiment.experimentId);
    await workflowStore.fetchWorkflow(this.experiment.experimentId);
    this.elements = workflowStore.elements;


    const bioBuddyStore = useBioBuddyStore();

    this.biobuddyWorkflowCallBack = async (data: any) => {
      await workflowStore.adjustWorkflow(data);
    };

    bioBuddyStore.addWorkflowAdjustmentEventHandler(this.biobuddyWorkflowCallBack);

    this.connectWebSocket();

    // Set up listener for 'component_jobs' event
    this.socket?.on('component_jobs', async (data: { component_id: string; job_ids: string[] }) => {
      if (data.component_id && data.job_ids) {
        // Call workflowStore method to adjust the component's job list
        workflowStore.adjustComponentJobsList(data.component_id, data.job_ids);
      }
    });

    // Listen for 'component_started' event
    this.socket.on('component_started', async (data: { component_id: string }) => {
      if (data.component_id) {
        workflowStore.updateComponentState(data.component_id, ComponentStateEnum.RUNNING);
      }
    });

    // Listen for 'component_finished' event
    this.socket.on('component_finished', async (data: { component_id: string }) => {
      if (data.component_id) {
        const componentStatus = await getComponentState(data.component_id);
        if (componentStatus) {
          workflowStore.updateComponentState(data.component_id, componentStatus.state, componentStatus.state_message);
        }
      }
    });

    // Listen for job_started event
    this.socket.on('job_started', async (data: { component_id: string, job_id: string }) => {
      if (data.component_id && data.job_id) {
        // Call workflowStore to update job status to RUNNING
        workflowStore.updateJobStatus(data.component_id, data.job_id, JobStateEnum.RUNNING);
      }
    });

    // Listen for job_finished event
    this.socket.on('job_finished', async (data: { component_id: string, job_id: string }) => {
      if (data.component_id && data.job_id) {
        // Call workflowStore to update job status to COMPLETED
        workflowStore.updateJobStatus(data.component_id, data.job_id, JobStateEnum.COMPLETED);
      }
    });

  },
  methods: {
    connectWebSocket() {
      const workflowStore = useWorkflowStore();

      // Create a new socket connection using Socket.IO
      this.socket = io('ws://127.0.0.1:8000', {transports: ['websocket', 'polling']});

      // When connected, join a room using the experimentId
      this.socket.on('connect', () => {
        console.log('Connected to Socket.IO server');
        if (this.experiment.experimentId) {
          this.socket.emit('join_room', { experiment_id: this.experiment.experimentId });
        }
      });

      // Handle disconnection
      this.socket.on('disconnect', () => {
        console.log('Disconnected from Socket.IO server');
      });
    },
    async checkAndCreateWorkflow() {
      const existingWorkflow = await getWorkflow(this.experiment.experimentId as string);

      if (!existingWorkflow) {
        await createWorkflow(this.experiment.experimentId as string);
      }
    },
    addComponent(option: any) {
      const workflowStore = useWorkflowStore();
      workflowStore.addComponent(option);
    },
    onConnect(params: { source: string, target: string, sourceHandle: string, targetHandle: string }) {
      const workflowStore = useWorkflowStore();
      workflowStore.onConnect(params);
    },
    onDeleteNode(nodeId: string) {
      const workflowStore = useWorkflowStore();
      workflowStore.onDeleteNode(nodeId);
    },
    openSettings(nodeId: string) {
      const workflowStore = useWorkflowStore();
      const node = workflowStore.getNodeById(nodeId);
      if (node) {
        this.selectedNode = node;
        this.sideMenuOpen = true;
      }
    },
    closeSideMenu() {
      this.sideMenuOpen = false;
    },
    closeModal() {
      this.modalOpen = false;
    },
    async startWorkflow() {
      this.isLocallyRunning = true;
      await startWorkflow(this.experiment.experimentId);
      setTimeout(() => {
        this.isLocallyRunning = false;
      }, 5000); // Reset isLocallyRunning after 5 seconds
    },
    onEdgeUpdate(params: { edge: Edge }) {
      const workflowStore = useWorkflowStore();
      workflowStore.onEdgeRemove(params.edge.id);
    },
    onNodeDragStopHandler(event: { node: Node }) {
      const workflowStore = useWorkflowStore();
      workflowStore.onNodeDragStopHandler(event);
    },
    openNodeDialog(nodeId: string) {
      const workflowStore = useWorkflowStore();
      const node = workflowStore.getNodeById(nodeId);
      if (node) {
        this.selectedNode = node;
        this.modalOpen = true;
      }
    },
  },
  beforeUnmount() {
    if (this.pollIntervalId !== null) {
      clearInterval(this.pollIntervalId);
    }
  },
  unmounted() {
    const bioBuddyStore = useBioBuddyStore();
    const index = bioBuddyStore.workflowAdjustmentEventHandlers.indexOf(this.biobuddyWorkflowCallBack!);
    if (index !== -1) {
      bioBuddyStore.workflowAdjustmentEventHandlers.splice(index, 1);
    }
  }
});
</script>

<style>
body {
  overflow: hidden;
}

.map-container {
  width: 100vw;
  height: 100vh;
}

.workflow {
  height: 100%;
  width: 100%;
}
</style>
