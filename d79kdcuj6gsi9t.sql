-- Adminer 4.6.3-dev PostgreSQL dump

\connect "d79kdcuj6gsi9t";

DROP TABLE IF EXISTS "checkin";
DROP SEQUENCE IF EXISTS checkin_id_seq;
CREATE SEQUENCE checkin_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."checkin" (
    "id" integer DEFAULT nextval('checkin_id_seq') NOT NULL,
    "login_id" integer,
    "loc" integer,
    "comment" character varying,
    CONSTRAINT "checkin_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "checkin_loc_fkey" FOREIGN KEY (loc) REFERENCES location(id) NOT DEFERRABLE,
    CONSTRAINT "checkin_login_id_fkey" FOREIGN KEY (login_id) REFERENCES users(id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "location";
DROP SEQUENCE IF EXISTS location_id_seq;
CREATE SEQUENCE location_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."location" (
    "id" integer DEFAULT nextval('location_id_seq') NOT NULL,
    "zipcode" character(5) NOT NULL,
    "city" character varying NOT NULL,
    "state" character varying NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "location_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "login_id" character varying NOT NULL,
    "password" character varying NOT NULL,
    "firstname" character varying NOT NULL,
    "lastname" character varying NOT NULL,
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
) WITH (oids = false);


-- 2018-07-12 02:49:07.68+00
