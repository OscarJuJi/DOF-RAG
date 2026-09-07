<template>
  <div class="clase">
    <BarraNavegacion :welcomeMessage="welcomeMessage" />
    <div class="content-container">
      <button class="add-employee-btn" @click="openCreateModal">
        Agregar empleado
      </button>
      <NewUser
        v-if="isModalVisible"
        :visible="isModalVisible"
        @close="closeCreateModal"
      />
      <div class="table-container">
        <table class="employee-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Número Telefónico</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="employee in employees" :key="employee.correo">
              <td>{{ employee.nombre }} {{ employee.appat }}</td>
              <td>{{ employee.correo }}</td>
              <td>{{ employee.telefono }}</td>
              <td>
                <button class="modify-btn" @click="openEditModal(employee)">
                  Modificar
                </button>
                <button class="delete-btn" @click="deleteEmployee(employee)">
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showEditModal" class="modal-overlay1" @click="toggleEditModal">
      <div class="modal-content" @click.stop>
        <i class="bx bx-user-circle user-avatar"></i>
        <h3>Modificar Datos del Usuario</h3>
        <form @submit.prevent="updateUser">
          <div class="contenedorNombre">
            <div class="field">
              <p>Nombre</p>
              <div>
                <input
                  class="input"
                  type="text"
                  v-model="editedUser.nombre"
                  required
                />
              </div>
            </div>
            <div class="field">
              <p>Apellido paterno</p>
              <div>
                <input
                  class="input"
                  type="text"
                  v-model="editedUser.appat"
                  required
                />
              </div>
            </div>
            <div class="field">
              <p>Apellido materno</p>
              <div>
                <input
                  class="input"
                  type="text"
                  v-model="editedUser.apmat"
                  required
                />
              </div>
            </div>
          </div>
          <div class="contenedorTelefono">
            <p>Departamento</p>
            <div>
              <i class="bx bx-briefcase"></i>
              <select v-model="editedUser.departamento" id="departamento">
                <option value="" disabled>Seleccione una opción</option>
                <option value="tesoreria">Tesorería</option>
                <option value="juridica">Jurídico</option>
                <option value="sistemas">Sistemas</option>
                <option value="contraloria">Contraloría</option>
                <option value="contabilidad">Contabilidad</option>
              </select>
            </div>
          </div>
          <div class="contenedorTelefono">
            <p>Teléfono</p>
            <div>
              <input
                class="input"
                type="text"
                v-model="editedUser.telefono"
                required
              />
            </div>
          </div>
          <div class="contenedorTelefono">
            <p>Recibir notificaciones</p>
            <div>
              <label class="switch">
                <input
                  type="checkbox"
                  v-model="editedUser.notif"
                  true-value="true"
                  false-value="false"
                />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          <div class="botonesMid">
            <div class="field">
              <button type="submit" :disabled="loading">
                <span v-if="loading">
                  <i class="bx bx-loader bx-spin"></i> Guardando...
                </span>
                <span v-else> Guardar </span>
              </button>
            </div>
            <div class="field">
              <button @click="toggleEditModal">Cancelar</button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import BarraNavegacion from '@/components/BarraNavegacion.vue';
import NewUser from './NewUser.vue';
import axios from 'axios';
import Swal from 'sweetalert2';

export default {
  name: 'EmpleadosView',
  components: {
    BarraNavegacion,
    NewUser,
  },
  data() {
    return {
      showCreateModal: false,
      isModalVisible: false,
      showEditModal: false,
      showModal: false,
      menuActive: false,
      employees: [],
      modalData: {
        name: '',
        department: '',
        phone: '',
      },
      editedUser: {
        nombre: '',
        appat: '',
        apmat: '',
        telefono: '',
        departamento: '',
        notif: false,
      },
      newUserData: {
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        phone: '',
        department: '',
        interests: [],
      },
      showNotifications: false,
      showUserMenu: false,
      welcomeMessage: 'Gestión de Empleados',
      loading: false,
    };
  },
  methods: {
    fetchEmployees() {
      axios
        .post('/api/usuarios')
        .then((response) => {
          this.employees = response.data;
        })
        .catch(() => {});
    },
    openEditModal(employee) {
      this.editedUser = { ...employee };
      this.showEditModal = true;
    },
    deleteEmployee(employee) {
      Swal.fire({
        title: '¿Estás seguro?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
      }).then((result) => {
        if (result.isConfirmed) {
          axios
            .delete('/api/delete_user', {
              params: {
                correo: employee.correo,
              },
            })
            .then(() => {
              Swal.fire(
                'Eliminado',
                'El empleado ha sido eliminado',
                'success',
              );
              this.fetchEmployees();
            })
            .catch(() => {});
        }
      });
    },
    toggleEditModal() {
      this.showEditModal = !this.showEditModal;
    },
    updateUser() {
      this.loading = true;
      axios
        .post('/api/actualizar_user', this.editedUser)
        .then((response) => {
          Swal.fire('Guardado', response.data.message, 'success');
          this.loading = false;
          this.toggleEditModal();
          this.fetchEmployees();
        })
        .catch(() => {
          this.loading = false;
        });
    },
    openCreateModal() {
      this.isModalVisible = true;
    },
    closeCreateModal() {
      this.isModalVisible = false;
    },
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
              this.$router.push('/employees-view');
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
  },
  mounted() {
    this.checkAuthentication();
    this.fetchEmployees();
    window.addEventListener('resize', this.handleResize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize);
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

.icon {
  color: #555;
  font-size: 35px;
  cursor: pointer;
}

.icon:hover {
  color: #222;
}

.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.add-employee-btn {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 10px 0;
  cursor: pointer;
  border-radius: 8px;
}

.table-container {
  overflow-x: auto;
}

.add-employee-btn:hover {
  background-color: #45a049;
}

.employee-table {
  width: 100%;
  border-collapse: collapse;
}

.employee-table th,
.employee-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.employee-table th {
  background-color: #f2f2f2;
}

.modify-btn {
  background-color: #008cba;
  border: none;
  color: white;
  padding: 5px 10px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  margin: 2px 1px;
  cursor: pointer;
  border-radius: 8px;
}

.modify-btn:hover {
  background-color: #007bb5;
}

.delete-btn {
  background-color: #f44336;
  border: none;
  color: white;
  padding: 5px 10px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 14px;
  margin: 2px 1px;
  cursor: pointer;
  border-radius: 8px;
}

.delete-btn:hover {
  background-color: #e53935;
}

.icon {
  color: #555;
  font-size: 35px;
}

.icon:hover {
  color: #222;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: none;
  padding: 20px;
  border-radius: 8px;
  width: 800px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
}

.create-user-modal {
  width: 900px;
  height: 620px;
}

.close-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 24px;
  cursor: pointer;
}

.modal-content {
  text-align: center;
}

.user-avatar {
  font-size: 60px;
  margin-bottom: 10px;
}

.user-name {
  font-size: 24px;
  margin-bottom: 20px;
}

.modal-content label {
  display: block;
  text-align: left;
  margin-bottom: 5px;
  font-weight: bold;
}

.modal-content input,
.modal-content .checkbox-group {
  width: calc(100% - 20px);
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.checkbox-group {
  display: flex;
  align-items: flex-start;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
}

.save-btn {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 10px 0;
  cursor: pointer;
  border-radius: 8px;
}

.save-btn:hover {
  background-color: #45a049;
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

  .content-container {
    padding: 10px;
  }

  .add-employee-btn {
    width: 100%;
    font-size: 14px;
    padding: 8px;
  }

  .table-container {
    overflow-x: auto;
  }

  .employee-table th,
  .employee-table td {
    font-size: 14px;
    padding: 6px;
  }

  .modify-btn,
  .delete-btn {
    font-size: 12px;
    padding: 4px 8px;
  }

  .modal {
    width: 90%;
    padding: 10px;
  }

  .create-user-modal {
    width: 95%;
    height: auto;
  }

  .modal-content input,
  .modal-content .checkbox-group {
    font-size: 14px;
    padding: 5px;
  }

  .modal-content .checkbox-group label {
    font-size: 12px;
  }

  .modal-content .checkbox-group input[type='checkbox'] {
    width: 16px;
    height: 16px;
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
  .content-container {
    padding: 20px;
  }

  .add-employee-btn {
    width: auto;
    font-size: 16px;
    padding: 10px 20px;
  }

  .table-container {
    overflow-x: auto;
  }

  .employee-table th,
  .employee-table td {
    font-size: 16px;
    padding: 8px;
  }

  .modify-btn,
  .delete-btn {
    font-size: 14px;
    padding: 6px 10px;
  }

  .modal {
    width: 75%;
    padding: 15px;
  }

  .create-user-modal {
    width: 80%;
    height: auto;
  }

  .modal-content input,
  .modal-content .checkbox-group {
    width: calc(100% - 15px);
  }
}
</style>
