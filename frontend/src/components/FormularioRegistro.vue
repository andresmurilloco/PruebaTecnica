<template>
  <div>
    <h1>Registrarse</h1>
    <form @submit.prevent="register">
      <div>
        <label for="fullName">Usuario:</label>
        <input type="text" id="fullName" v-model="fullName" required />
      </div>
      <div>
        <label for="email">Correo electrónico:</label>
        <input type="email" id="email" v-model="email" required />
      </div>
      <div>
        <label for="password">Contraseña:</label>
        <input type="password" id="password" v-model="password" required />
      </div>
      <div>
        <label for="confirmPassword">Confirmar contraseña:</label>
        <input type="password" id="confirmPassword" v-model="confirmPassword" required />
      </div>
      <button type="submit" :disabled="isLoading">{{ isLoading ? 'Cargando...' : 'Registrarse' }}</button>
      <p v-if="registerError" style="color: red;">Hubo un error al registrar el usuario. Intenta nuevamente.</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      fullName: '',
      email: '',
      password: '',
      confirmPassword: '',
      registerError: false,
      isLoading: false, // Estado para la carga
    };
  },
  methods: {
    async register() {
      if (this.password !== this.confirmPassword) {
        this.registerError = true;
        return;
      }
      
      this.isLoading = true; // Activar carga
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/registro/', {
          username: this.fullName,
          email: this.email,
          password: this.password,
        });
        
        this.$emit('registrationSuccess');
        this.isLoading = false; // Desactivar carga
      } catch (error) {
        console.error('Error al registrar el usuario:', error);
        this.registerError = true;
        this.isLoading = false; // Desactivar carga
      }
    },
  },
};
</script>

<style scoped>
/* Agregar estilos para el formulario de registro */
form {
  width: 100%;
  max-width: 600px;
  margin: 20px auto;
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

form div {
  margin-bottom: 15px;
}

form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

form input {
  width: 100%;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

form button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  font-size: 16px;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}

form button:hover {
  background-color: #38a369;
}

form p {
  color: #e74c3c; /* Color rojo para mensajes de error */
}
</style>
