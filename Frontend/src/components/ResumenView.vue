<template>
  <div class="clase">
    <BarraNavegacion :welcomeMessage="welcomeMessage" />

    <div class="main-content">
      <div class="content">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>Codigo del diario</th>
                <th>Fecha del diario</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(summary, index) in summaries" :key="index">
                <td>{{ summary.codigo }}</td>
                <td>{{ getSummaryDate(summary) }}</td>
                <td>
                  <button class="btn-view" @click="showSummary(summary)">
                    Ver resumen
                  </button>
                  <button
                    class="btn-download"
                    @click="openDof(getSummaryDate(summary))"
                  >
                    Consultar DOF original
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="isModalVisible" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeModal">&times;</span>
        <h2>Resumen del DOF</h2>
        <p class="summary-content">{{ selectedSummary }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import BarraNavegacion from './BarraNavegacion.vue';
import axios from 'axios';

export default {
  name: 'ResumenView',
  data() {
    return {
      welcomeMessage: 'Listado de resúmenes',
      summaries: [],
      isModalVisible: false,
      selectedSummary: '',
    };
  },
  components: {
    BarraNavegacion,
  },
  methods: {
    handleResize() {
      if (window.innerWidth > 768 && this.menuActive) {
        this.menuActive = false;
      } else if (window.innerWidth < 1024) {
        this.menuActive = false;
      }
    },
    checkAuthentication() {
      if (!localStorage.getItem('token')) {
        this.$router.push('/');
      } else {
        axios
          .post('/api/validar_token', {
            token: localStorage.getItem('token'),
          })
          .then((response) => {
            if (response.data.valid) {
              this.$router.push('/resumen-view');
            } else {
              localStorage.removeItem('token');
              this.$router.push('/');
            }
          })
          .catch(() => {
            this.$router.push('/');
          });
      }
    },
    fetchSummaries() {
      axios
        .get('/remuenes.json')
        .then((response) => {
          this.summaries = response.data;
        })
        .catch(() => {});
    },
    getSummaryDate(summary) {
      return Object.keys(summary).find((key) => key !== 'codigo');
    },
    showSummary(summary) {
      const date = this.getSummaryDate(summary);
      this.selectedSummary = summary[date];
      this.isModalVisible = true;
    },
    closeModal() {
      this.isModalVisible = false;
    },
    openDof(date) {
      const url = `https://sidof.segob.gob.mx/welcome/${date}`;
      window.open(url, '_blank');
    },
    handleKeydown(event) {
      if (event.key === 'Escape') {
        this.closeModal();
      }
    },
    handleOutsideClick(event) {
      if (event.target.classList.contains('modal')) {
        this.closeModal();
      }
    },
  },
  mounted() {
    this.checkAuthentication();
    this.fetchSummaries();
    window.addEventListener('resize', this.handleResize);
    document.addEventListener('keydown', this.handleKeydown);
    document.addEventListener('click', this.handleOutsideClick);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
    document.removeEventListener('keydown', this.handleKeydown);
    document.removeEventListener('click', this.handleOutsideClick);
  },
};
</script>
<style>
.modal {
  display: block;
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  background-color: rgb(0, 0, 0);
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 5% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 80%;
  max-height: 98vh;
  text-align: justify;
  overflow-y: auto;
}
.modal-body {
  max-height: 70vh;
  overflow-y: auto;
}

.summary-content {
  white-space: pre-line;
}

.close {
  position: absolute;
  top: 70px;
  right: 650px;
  color: #aaa;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

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
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.search-container {
  margin-bottom: 20px;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.content {
  display: flex;
  justify-content: space-between;
}

.table-container {
  flex: 3;
  margin-right: 20px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th,
td {
  padding: 10px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f2f2f2;
}

td {
  background-color: #fff;
}

.btn-view {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 5px 10px;
  margin-right: 5px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-view:hover {
  background-color: #0056b3;
}

.btn-download {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-download:hover {
  background-color: #b02a37;
}

.calendar-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.calendar-container h2 {
  margin-bottom: 10px;
}

.calendar-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.icon {
  color: #555;
  font-size: 35px;
}

.icon:hover {
  color: #222;
}

.calendar-container.small-screen-calendar {
  display: none;
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

  .content {
    flex-direction: column;
  }

  .table-container {
    margin-right: 0;
    margin-bottom: 20px;
  }

  .calendar-container.small-screen-calendar {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;
  }

  .calendar-container.large-screen-calendar {
    display: none;
  }

  .calendar-input {
    width: calc(100% - 20px);
    margin: 0 10px;
  }

  .search-container {
    width: 100%;
  }

  .search-input {
    width: calc(100% - 40px);
    margin: 0 10px;
  }

  .btn-view,
  .btn-download {
    display: block;
    width: calc(100% - 20px);
    margin: 10px auto;
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

  .content {
    flex-direction: column;
  }

  .table-container {
    margin-right: 0;
    margin-bottom: 20px;
  }

  .calendar-container.small-screen-calendar {
    display: none;
  }

  .calendar-container.large-screen-calendar {
    display: flex;
  }

  .calendar-container {
    width: 100%;
  }

  .calendar-input {
    width: calc(100% - 20px);
    margin: 0 10px;
  }

  .search-container {
    width: 100%;
  }

  .search-input {
    width: calc(100% - 20px);
    margin: 0 10px;
  }

  .btn-view,
  .btn-download {
    display: block;
    width: calc(100% - 20px);
    margin: 10px auto;
  }
}
</style>
