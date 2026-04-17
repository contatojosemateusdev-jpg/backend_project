# Sistema de Agendamento - Requisitos                                         
                                                                                                                   
  ## Objetivo                                                                
  Criar uma API para gestão de agendamentos de serviços (Barbearia), permitindo que clientes marquem horários e administradores gerenciem serviços e profissionais.                                                   
                                        
  ## Requisitos Funcionais                                                                
  - [ ] **Gestão de Usuários:** Cadastro e autenticação de clientes e admins.   
  - [ ] **Gestão de Catálogo:** CRUD de serviços (nome, preço, duração) e profissionais.                           
  - [ ] **Agendamento:** Permitir a marcação de data/hora vinculando Cliente, Profissional e Serviço.              
  - [ ] **Validação de Conflitos:** Impedir que dois agendamentos ocorram no mesmo horário para o mesmo            
  profissional.                                                                                                    
  - [ ] **Consulta:** Listar agendamentos do dia/semana.                                                           
                                                                                
  ## Requisitos Não Funcionais                                                                       
  - API desenvolvida com Python e FastAPI.                                      
  - Banco de dados relacional (SQLite para desenvolvimento).                                                       
  - Documentação automática Swagger.     