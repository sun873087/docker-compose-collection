// @ts-ignore
const Keycloak = window.Keycloak;

const keycloak = new Keycloak({
  url: 'http://localhost:8080',  // Keycloak 伺服器 URL
  realm: 'sam-test',             // 你的 realm 名稱
  clientId: 'myclient',         // 你的 client ID
});

export default keycloak;