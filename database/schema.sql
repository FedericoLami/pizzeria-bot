CREATE TABLE productos(
    idProducto SERIAL PRIMARY KEY,
    nombreProducto VARCHAR(50),
    monto DOUBLE PRECISION,
    disponible boolean
);

CREATE TABLE pedido(
    idPedido SERIAL PRIMARY KEY,
    sessionId VARCHAR(50),
    fecha DATE,
    horaPedido TIME,
    horaEstimada TIME,
    horaEntrega TIME NULL
);

CREATE TABLE detallePedido(
    idDetalle SERIAL PRIMARY KEY,
    idPedido INT REFERENCES pedido(idPedido),
    idProducto INT REFERENCES productos(idProducto),
    cantidad INT
);

CREATE TABLE reclamos(
    idReclamo SERIAL PRIMARY KEY,
    idPedido INT REFERENCES pedido(idPedido),
    idDetalle INT REFERENCES detallePedido(idDetalle),
    motivo VARCHAR(140),
    fecha DATE
);

CREATE TABLE reembolsos(
    idReembolso SERIAL PRIMARY KEY,
    idPedido INT REFERENCES pedido(idPedido),
    idDetalle INT REFERENCES detallePedido(idDetalle),
    monto DOUBLE PRECISION,
    motivo VARCHAR(140),
    fecha DATE
);