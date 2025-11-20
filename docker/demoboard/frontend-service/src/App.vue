<template>
  <div>
    <input v-model="title"/>
    <button @click="addTask">Ajouter</button>

    <div v-for="t in tasks" :key="t.id">
      {{ t.title }} - {{ t.status }}
      <button @click="startJob(t.id)">Start</button>
    </div>
  </div>
</template>

<script>
export default {
  data(){ return { tasks:[], title:"" } },
  mounted(){ this.load() },
  methods:{
    async load(){
      this.tasks = await fetch("/api/tasks").then(r=>r.json())
    },
    async addTask(){
      await fetch("/api/tasks",{method:"POST", body:JSON.stringify({title:this.title})})
      this.load()
    },
    async startJob(id){
      await fetch(`/api/tasks/${id}/start-job`,{method:"POST"})
      this.load()
    }
  }
}
</script>
