<template>
  <div class="clase">
    <BarraNavegacion :welcomeMessage="welcomeMessage" />
    <div class="main-content">
      <div class="main-left">
        <h2>Archivo local del DOF</h2>
        <p v-if="status">
          {{ status.documents }} documentos y {{ status.chunks }} fragmentos
          disponibles.
        </p>
        <p>{{ statusMessage }}</p>
        <p>
          Las respuestas se basan en los documentos cargados. El archivo
          incluido es histórico y no se actualiza automáticamente.
        </p>
        <router-link to="/consult-view">Consultar el archivo</router-link>
      </div>
      <div class="main-right">
        <h2>Documentos disponibles</h2>
        <div class="dof-summary">
          <p v-if="!documents.length">Todavía no hay documentos indexados.</p>
          <ul>
            <li v-for="document in documents" :key="document.id">
              {{ document.name }} · {{ document.pages }} páginas
            </li>
          </ul>
          <router-link to="/resumen-view"
            >Ver documentos y resúmenes</router-link
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarraNavegacion from '@/components/BarraNavegacion.vue';
import axios from 'axios';

export default {
  name: 'NotificationView',
  components: { BarraNavegacion },
  data() {
    return {
      welcomeMessage: 'Archivo local y estado del servicio',
      status: null,
      documents: [],
      statusMessage: 'Comprobando el servicio local…',
    };
  },
  methods: {
    async fetchStatus() {
      try {
        const [status, documents] = await Promise.all([
          axios.get('/api/status'),
          axios.get('/api/documents'),
        ]);
        this.status = status.data;
        this.documents = documents.data;
        this.statusMessage = status.data.ready
          ? 'El buscador local está listo.'
          : 'El buscador necesita que Ollama y el índice estén preparados.';
      } catch (error) {
        if (error.response?.status === 401) this.$router.push('/');
        this.statusMessage = 'No se pudo consultar el estado del servicio.';
      }
    },
  },
  mounted() {
    this.fetchStatus();
  },
};
</script>

<style>
.clase {
  margin: 0;
  width: 100%;
}

.welcome-text {
  background-color: #c7eef3;
  width: 100%;
  border: 1px solid #000;
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  overflow-x: hidden;
}

.welcome-text .text-container {
  max-width: 100%;
  width: 100%;
  padding: 0 20px 0 130px;
  box-sizing: border-box;
}

.welcome-text h1 {
  padding-top: 20px;
  padding-bottom: 20px;
  margin: 0;
  text-align: left;
  word-break: break-word;
}

.main-content {
  display: flex;
  justify-content: space-between;
  margin: 20px auto;
  max-width: 1500px;
  height: auto;
  padding: 20px;
}

.main-left,
.main-right {
  box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  box-sizing: border-box;
  border-radius: 8px;
  height: auto;
  overflow: hidden;
}

.main-left {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  flex: 4;
  margin-right: 20px;
  min-height: 400px;
}

.main-right {
  background-color: #fff;
  color: #fff;
  flex: 2;
  background-color: #007bff;
  display: flex;
  flex-direction: column;
  height: auto;
}

h2 {
  margin-top: 0;
  margin-bottom: 0;
}

ul {
  list-style-type: disc;
  padding-left: 20px;
}

.dof-summary {
  color: #fff;
  padding: 10px;
  border-radius: 4px;
  max-height: 200px;
}

.dof-summary p {
  background-color: #fff;
  color: #000;
  padding: 10px;
  border-radius: 4px;
  margin: 0;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
  box-sizing: border-box;
  text-align: justify;
}

.icon {
  color: #555;
  font-size: 35px;
  cursor: pointer;
}

.icon:hover {
  color: #222;
}

@media (max-width: 768px) {
  .navbar-burger {
    display: block;
  }

  .welcome-text {
    text-align: center;
  }

  .welcome-navbar .navbar-menu-1 {
    display: none;
  }

  .navbar-menu {
    display: none;
    padding-top: 0px;
    padding-bottom: 5px;
  }

  .navbar-end {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20px;
  }

  .navbar-menu.is-active {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .navbar-item {
    margin-left: 0;
    margin-bottom: 10px;
    width: 100%;
    text-align: center;
  }

  .navbar-icons {
    margin-left: auto;
  }

  .main-content {
    flex-direction: column;
    padding: 10px;
  }

  .main-left {
    margin-right: 0;
    margin-bottom: 20px;
    height: auto;
  }

  .main-right {
    max-width: 100%;
    height: auto;
  }

  .welcome-text .text-container {
    padding: 0 20px;
  }

  .welcome-text h1 {
    text-align: center;
  }
}

@media (min-width: 768px) and (max-width: 1024px) {
  .navbar-burger {
    display: block;
  }

  .welcome-navbar .navbar-menu-1 {
    display: none;
  }

  .navbar-menu {
    display: none;
  }

  .navbar-menu.is-active {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
  }

  .navbar-item {
    margin-left: 0;
    margin-bottom: 10px;
    width: 100%;
    text-align: center;
  }

  .navbar-icons {
    margin-left: auto;
  }

  .main-content {
    flex-direction: column;
    padding: 10px;
  }

  .main-left {
    margin-right: 0;
    margin-bottom: 20px;
    height: auto;
  }

  .main-right {
    max-width: 100%;
    height: auto;
  }

  .welcome-text .text-container {
    padding: 0 20px;
  }

  .welcome-text h1 {
    text-align: center;
  }
}
</style>
