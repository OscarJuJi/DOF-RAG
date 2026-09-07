<template>
  <div class="clase">
    <BarraNavegacion :welcomeMessage="welcomeMessage" />

    <div class="search-container">
      <input
        type="text"
        class="search-input"
        placeholder="¿Qué deseas consultar en el DOF?"
        v-model="searchText"
        @keypress.enter="performSearch"
      />
      <button class="search-btn" :disabled="isLoading" @click="performSearch">
        <i v-if="!isLoading" class="bx bx-search-alt-2"></i>
        <i v-else class="bx bx-loader bx-spin"></i>
      </button>
    </div>
    <div class="main-content">
      <div class="results-container">
        <div class="history-container">
          <h2>
            Historial de navegación
            <button class="clear-btn" @click="confirmClearHistory">
              <i class="bx bx-trash"></i>
            </button>
          </h2>
          <transition-group name="results" tag="div">
            <div v-for="(entries, day) in groupedHistory" :key="day">
              <li class="day" @click="loadResultsForDay(day)">{{ day }}</li>
              <ul>
                <li v-if="entries.length > 0">{{ entries[0].question }}</li>
              </ul>
            </div>
          </transition-group>
        </div>

        <div class="filter-container">
          <div class="output-container">
            <transition-group tag="p" name="history">
              <div
                v-for="item in selectedResults"
                :key="item.id"
                class="query-result"
              >
                <p class="query-question">{{ item.question }}</p>
                <p class="query-answer">{{ item.answer }}</p>
              </div>
            </transition-group>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import BarraNavegacion from '@/components/BarraNavegacion.vue';
import axios from 'axios';
import Swal from 'sweetalert2';

export default {
  name: 'ConsultasView',
  data() {
    return {
      welcomeMessage: 'Consultas al DOF',
      searchText: '',
      queryResults: [],
      chatHistory: {},
      selectedResults: [],
      isLoading: false,
    };
  },
  components: {
    BarraNavegacion,
  },
  computed: {
    groupedHistory() {
      return this.groupHistoryByDay();
    },
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
              this.$router.push('/consult-view');
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
    confirmClearHistory() {
      Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción eliminará todo el historial de consultas.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        customClass: {
          confirmButton: 'custom-confirm-button-class',
          title: 'swal-title',
          content: 'swal-content',
          cancelButton: 'custom-cancel-button-class',
        },
      }).then((result) => {
        if (result.isConfirmed) {
          this.clearChatHistory();
          Swal.fire({
            title: 'Historial eliminado',
            text: 'El historial de consultas ha sido eliminado correctamente.',
            icon: 'success',
            customClass: {
              confirmButton: 'custom-confirm-button-class',
              title: 'swal-title',
              content: 'swal-content',
            },
          });
        }
      });
    },
    clearChatHistory() {
      const userId = localStorage.getItem('correo');
      localStorage.removeItem(`chatHistory_${userId}`);
      this.chatHistory = {};
      this.selectedResults = [];
      this.queryResults = [];
    },
    loadChatHistory() {
      const userId = localStorage.getItem('correo');
      const storedHistory = localStorage.getItem(`chatHistory_${userId}`);
      if (storedHistory) {
        this.chatHistory = JSON.parse(storedHistory);
      }
    },
    saveChatHistory() {
      const userId = localStorage.getItem('correo');
      localStorage.setItem(
        `chatHistory_${userId}`,
        JSON.stringify(this.chatHistory),
      );
    },
    groupHistoryByDay() {
      const grouped = {};
      for (const [date, entries] of Object.entries(this.chatHistory)) {
        const day = this.formatDate(new Date(date));
        if (!grouped[day]) {
          grouped[day] = [];
        }
        grouped[day].push(...entries);
      }
      return grouped;
    },
    formatDate(date) {
      const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      };
      return date.toLocaleDateString(undefined, options);
    },
    loadResultsForDay(day) {
      for (const [date, entries] of Object.entries(this.chatHistory)) {
        const formattedDate = this.formatDate(new Date(date));
        if (formattedDate === day) {
          this.selectedResults = entries;
          break;
        }
      }
    },
    performSearch() {
      if (this.searchText.trim() === '' || this.isLoading) return;

      this.isLoading = true;

      const question = this.searchText;
      const today = new Date().toISOString().split('T')[0];
      const tmpC = [];

      for (const [, entries] of Object.entries(this.chatHistory)) {
        tmpC.push(
          ...entries.map((entry) => ({
            question: entry.question,
            answer: entry.answer,
          })),
        );
      }
      const historyString = tmpC
        .map(
          (entry) => `Human: ${entry.question}\nCapiDOFChat: ${entry.answer}`,
        )
        .join('\n');

      const request = {
        input: {
          question: question,
          chat_history: historyString,
        },
      };

      axios
        .post('/modelo/query/invoke', request)
        .then((response) => {
          const answer = response.data.output;
          const newQuery = {
            id: Date.now(),
            question: question,
            answer: answer,
          };

          if (!this.chatHistory[today]) {
            this.chatHistory[today] = [];
          }

          this.chatHistory[today].push(newQuery);
          this.saveChatHistory();

          this.queryResults.push(newQuery);

          this.selectedResults = this.chatHistory[today];

          this.searchText = '';
          this.isLoading = false;
          setTimeout(() => {
            this.scrollToBottom();
          }, 100);
        })
        .catch(() => {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Ocurrió un error al realizar la consulta.',
            customClass: {
              confirmButton: 'custom-confirm-button-class',
              title: 'swal-title',
              content: 'swal-content',
            },
          });
          this.isLoading = false;
        });
    },
    scrollToBottom() {
      const outputContainer = this.$el.querySelector('.output-container');
      outputContainer.scrollTop = outputContainer.scrollHeight;
    },
  },
  mounted() {
    window.addEventListener('resize', this.handleResize);
    this.checkAuthentication();
    this.loadChatHistory();
    this.selectedResults =
      this.chatHistory[new Date().toISOString().split('T')[0]] || [];
    setTimeout(() => {
      this.scrollToBottom();
    }, 100);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
  },
};
</script>

<style>
.bx-loader {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
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
  display: flex;
  justify-content: space-between;
  margin: 20px auto;
  max-width: 1500px;
  height: 1500px;
  padding: 20px;
}
.search-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  position: fixed;
  bottom: 60px;
  width: 60%;
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
  z-index: 2;
  padding: 10px;
  justify-content: center;
  left: 50%;
  transform: translateX(-50%);
}

.search-input {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 8px 0 0 8px;
}

.search-btn {
  background-color: #007bff;
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border-radius: 0 8px 8px 0;
  height: 100%;
}

.search-btn i {
  font-size: 1.2rem;
}

.search-btn:hover {
  background-color: #0056b3;
}

.results-container {
  display: flex;
  flex-direction: row;
  height: 70%;
}

.history-container {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  padding: 20px;
  width: 200px;
  border-radius: 8px;
  margin-right: 20px;
  height: 300px;
  overflow-y: auto;
}

.history-container h2 {
  margin-top: 0;
  font-size: 1.2rem;
}

.history-container ul {
  list-style-type: none;
  padding: 0;
  font-size: 0.7rem;
}

.history-container li {
  margin-bottom: 10px;
}

.history-container .day {
  font-weight: bold;
  cursor: pointer;
}

.day:hover {
  text-decoration: underline;
}

.filter-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 1;
}

.filter-btn {
  background-color: #808080;
  border: none;
  color: white;
  padding: 10px;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 20px;
}

.filter-btn:hover {
  background-color: #4d4d4d;
}

.output-container {
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
  overflow-y: auto;
  height: 50%;
}

.output-container p {
  margin: 0;
}

.icon {
  color: #555;
  font-size: 35px;
}

.icon:hover {
  color: #222;
}

.query-result {
  margin-bottom: 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
}

.query-question {
  font-weight: bold;
  margin-bottom: 10px;
}

.query-answer {
  margin: 0;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 0 5px 2px #008cba;
  border-color: #008cba;
}

.results-enter-from {
  opacity: 0;
  transform: scale(0.6);
}

.results-enter-to {
  opacity: 1;
  transform: scale(1);
}

.results-enter-active {
  transition: all 0.4s ease;
}

.results-leave-from {
  opacity: 1;
  transform: scale(1);
}

.results-leave-to {
  opacity: 0;
  transform: scale(0.6);
}

.results-leave-active {
  transition: all 0.4s ease;
}

.history-enter-from {
  opacity: 0;
  transform: translateX(-50px);
}

.history-enter-to {
  opacity: 1;
  transform: translateX(0);
}

.history-enter-active {
  transition: all 0.6s ease;
}

.history-leave-from {
  opacity: 1;
  transform: translateX(0);
}

.history-leave-to {
  opacity: 0;
  transform: translateX(-50px);
}

.history-leave-active {
  transition: all 0.6s ease;
}

.swal-title {
  font-family: 'Arial', sans-serif;
  font-size: 24px;
  font-weight: bold;
}

.swal-content {
  font-family: 'Arial', sans-serif;
  font-size: 18px;
}

.custom-confirm-button-class {
  background-color: #3085d6 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 5px !important;
  padding: 10px 20px !important;
  font-size: 16px !important;
}

.custom-cancel-button-class {
  background-color: #d33 !important;
  color: #fff !important;
  border: none !important;
  border-radius: 5px !important;
  padding: 10px 20px !important;
  font-size: 16px !important;
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

  .search-container {
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    bottom: 100px;
    width: 96.5%;
  }

  .search-input {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 8px 0 0 8px;
    height: 100%;
  }

  .search-btn {
    border: none;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    border-radius: 0 8px 8px 0;
    height: 100%;
  }

  .search-btn i {
    font-size: 1.2rem;
  }

  .results-container {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    height: 70%;
  }

  .history-container {
    display: none;
    width: 100%;
    margin-bottom: 20px;
  }

  .welcome-text .text-container {
    padding: 0 20px;
  }

  .welcome-text h1 {
    text-align: center;
  }

  .search-container,
  .filter-container,
  .results-container,
  .output-container,
  .history-container {
    box-sizing: border-box;
    overflow-x: hidden;
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
    height: 100%;
  }

  .search-container {
    flex-direction: row;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    background-color: #fff;
    border: 1px solid #ddd;
    border-radius: 8px;
    bottom: 100px;
    bottom: 100px;
    width: 97.5%;
  }

  .search-input {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 8px 0 0 8px;
    height: 100%;
  }

  .search-btn {
    border: none;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    border-radius: 0 8px 8px 0;
    height: 100%;
  }

  .search-btn i {
    font-size: 1.2rem;
  }

  .results-container {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    width: 100%;
  }

  .history-container {
    display: none;
    width: 100%;
    margin-bottom: 20px;
  }

  .output-container {
    width: 100%;
  }

  .welcome-text .text-container {
    padding: 0 20px;
  }

  .welcome-text h1 {
    text-align: center;
  }

  .search-container,
  .filter-container,
  .results-container,
  .output-container,
  .history-container {
    box-sizing: border-box;
    overflow-x: hidden;
  }
}
.clear-btn {
  background: none;
  border: none;
  color: red;
  cursor: pointer;
  margin-left: 10px;
  font-size: 24px;
  padding: 10px;
}

.clear-btn:hover {
  color: darkred;
}

.clear-btn i {
  font-size: inherit;
}

.custom-confirm-button-class {
  background-color: #007bff !important;
  border-color: #007bff !important;
  color: #fff !important;
}
</style>
