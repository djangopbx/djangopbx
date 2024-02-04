--
-- PostgreSQL database dump
--

-- Dumped from database version 15.5 (Debian 15.5-0+deb12u1)
-- Dumped by pg_dump version 15.5 (Debian 15.5-0+deb12u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agents; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.agents (
   uuid text,
   name text,
   instance_id text,
   type text,
   contact text,
   status text,
   state text,
   max_no_answer integer DEFAULT 0 NOT NULL,
   wrap_up_time integer DEFAULT 0 NOT NULL,
   reject_delay_time integer DEFAULT 0 NOT NULL,
   busy_delay_time integer DEFAULT 0 NOT NULL,
   no_answer_delay_time integer DEFAULT 0 NOT NULL,
   last_bridge_start integer DEFAULT 0 NOT NULL,
   last_bridge_end integer DEFAULT 0 NOT NULL,
   last_offered_call integer DEFAULT 0 NOT NULL,
   last_status_change integer DEFAULT 0 NOT NULL,
   no_answer_count integer DEFAULT 0 NOT NULL,
   calls_answered integer DEFAULT 0 NOT NULL,
   talk_time integer DEFAULT 0 NOT NULL,
   ready_time integer DEFAULT 0 NOT NULL,
   external_calls_count INTEGER NOT NULL DEFAULT 0,
   agent_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.agents OWNER TO freeswitch;


--
-- Name: aliases; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.aliases (
    sticky integer,
    alias text,
    command text,
    hostname text,
    alias_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.aliases OWNER TO freeswitch;

--
-- Name: calls; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.calls (
    call_uuid uuid PRIMARY KEY default gen_random_uuid(),
    call_created text,
    call_created_epoch integer,
    caller_uuid text,
    callee_uuid text,
    hostname text
);
ALTER TABLE public.calls OWNER TO freeswitch;

--
-- Name: channels; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.channels (
    channel_uuid uuid PRIMARY KEY default gen_random_uuid(),
    uuid text,
    direction text,
    created text,
    created_epoch integer,
    name text,
    state text,
    cid_name text,
    cid_num text,
    ip_addr text,
    dest text,
    application text,
    application_data text,
    dialplan text,
    context text,
    read_codec text,
    read_rate text,
    read_bit_rate text,
    write_codec text,
    write_rate text,
    write_bit_rate text,
    secure text,
    hostname text,
    presence_id text,
    presence_data text,
    accountcode text,
    callstate text,
    callee_name text,
    callee_num text,
    callee_direction text,
    call_uuid text,
    sent_callee_name text,
    sent_callee_num text,
    initial_cid_name text,
    initial_cid_num text,
    initial_ip_addr text,
    initial_dest text,
    initial_dialplan text,
    initial_context text
);
ALTER TABLE public.channels OWNER TO freeswitch;

--
-- Name: complete; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.complete (
sticky integer,
    a1 text,
    a2 text,
    a3 text,
    a4 text,
    a5 text,
    a6 text,
    a7 text,
    a8 text,
    a9 text,
    a10 text,
    hostname text,
    complete_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.complete OWNER TO freeswitch;

--
-- Name: db_data; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.db_data (
    hostname text,
    realm text,
    data_key text,
    data text,
    db_data_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.db_data OWNER TO freeswitch;

--
-- Name: db_data; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.fifo_outbound (
   uuid text,
   fifo_name text,
   originate_string text,
   simo_count integer,
   use_count integer,
   timeout integer,
   lag integer,
   next_avail integer not null default 0,
   expires integer not null default 0,
   static integer not null default 0,
   outbound_call_count integer not null default 0,
   outbound_fail_count integer not null default 0,
   hostname text,
   taking_calls integer not null default 1,
   status text,
   outbound_call_total_count integer not null default 0,
   outbound_fail_total_count integer not null default 0,
   active_time integer not null default 0,
   inactive_time integer not null default 0,
   manual_calls_out_count integer not null default 0,
   manual_calls_in_count integer not null default 0,
   manual_calls_out_total_count integer not null default 0,
   manual_calls_in_total_count integer not null default 0,
   ring_count integer not null default 0,
   start_time integer not null default 0,
   stop_time integer not null default 0,
   fifo_outbound_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.fifo_outbound OWNER TO freeswitch;

--
-- Name: db_data; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.fifo_bridge (
    fifo_name text not null,
    caller_uuid text not null,
    caller_caller_id_name text,
    caller_caller_id_number text,
    consumer_uuid text not null,
    consumer_outgoing_uuid text,
    bridge_start integer,
    fifo_bridge_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.fifo_bridge OWNER TO freeswitch;

--
-- Name: group_data; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.fifo_callers (
    fifo_name text not null,
    uuid text not null,
    caller_caller_id_name text,
    caller_caller_id_number text,
    timestamp integer,
    fifo_caller_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.fifo_callers OWNER TO freeswitch;

--
-- Name: group_data; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.group_data (
    hostname text,
    groupname text,
    url text,
    group_data_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.group_data OWNER TO freeswitch;

--
-- Name: interfaces; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.interfaces (
    type text,
    name text,
    description text,
    ikey text,
    filename text,
    syntax text,
    hostname text,
    interface_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.interfaces OWNER TO freeswitch;

--
-- Name: limit_data; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.limit_data (
    hostname text,
    realm text,
    id text,
    limit_data_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.limit_data OWNER TO freeswitch;

--
-- Name: members; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.members (
   queue text,
   instance_id text,
   uuid text NOT NULL,
   session_uuid text NOT NULL,
   cid_number text,
   cid_name text,
   system_epoch integer DEFAULT 0 NOT NULL,
   joined_epoch integer DEFAULT 0 NOT NULL,
   rejoined_epoch integer DEFAULT 0 NOT NULL,
   bridge_epoch integer DEFAULT 0 NOT NULL,
   abandoned_epoch integer DEFAULT 0 NOT NULL,
   base_score integer DEFAULT 0 NOT NULL,
   skill_score integer DEFAULT 0 NOT NULL,
   serving_agent text,
   serving_system text,
   state text,
   member_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.members OWNER TO freeswitch;

--
-- Name: nat; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.nat (
    sticky integer,
    port integer,
    proto integer,
    hostname text,
    nat_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.nat OWNER TO freeswitch;

--
-- Name: recovery; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.recovery (
    runtime_uuid text,
    technology text,
    profile_name text,
    hostname text,
    metadata text,
    uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.recovery OWNER TO freeswitch;

--
-- Name: registrations; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.registrations (
    reg_user text,
    realm text,
    token text,
    url text,
    expires integer,
    network_ip text,
    network_port text,
    network_proto text,
    hostname text,
    metadata text,
    registration_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.registrations OWNER TO freeswitch;

--
-- Name: sip_registrations; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_registrations (
    call_id text,
    sip_user text,
    sip_host text,
    presence_hosts text,
    contact text,
    status text,
    ping_status text,
    ping_count integer,
    ping_time bigint,
    force_ping integer,
    rpid text,
    expires bigint,
    ping_expires integer,
    user_agent text,
    server_user text,
    server_host text,
    profile_name text,
    hostname text,
    network_ip text,
    network_port text,
    sip_username text,
    sip_realm text,
    mwi_user text,
    mwi_host text,
    orig_server_host text,
    orig_hostname text,
    sub_host text,
    sip_registration_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_registrations OWNER TO freeswitch;

--
-- Name: sip_authentication; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_authentication (
    nonce text,
    expires bigint,
    profile_name text,
    hostname text,
    last_nc integer,
    algorithm integer DEFAULT 1 NOT NULL,
    sip_authentication_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_authentication OWNER TO freeswitch;

--
-- Name: sip_dialogs; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_dialogs (
    call_id text,
    uuid text,
    sip_to_user text,
    sip_to_host text,
    sip_from_user text,
    sip_from_host text,
    contact_user text,
    contact_host text,
    state text,
    direction text,
    user_agent text,
    profile_name text,
    hostname text,
    contact text,
    presence_id text,
    presence_data text,
    call_info text,
    call_info_state text DEFAULT ''::text,
    expires bigint DEFAULT 0,
    status text,
    rpid text,
    sip_to_tag text,
    sip_from_tag text,
    rcd integer DEFAULT 0 NOT NULL,
    sip_dialog_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_dialogs OWNER TO freeswitch;

--
-- Name: sip_presence; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_presence (
    sip_user text,
    sip_host text,
    status text,
    rpid text,
    expires bigint,
    user_agent text,
    profile_name text,
    hostname text,
    network_ip text,
    network_port text,
    open_closed text,
    sip_presence_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_presence OWNER TO freeswitch;

--
-- Name: sip_shared_appearance_dialogs; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_shared_appearance_dialogs (
    profile_name text,
    hostname text,
    contact_str text,
    call_id text,
    network_ip text,
    expires bigint,
    sip_shared_appearance_dialog_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_shared_appearance_dialogs OWNER TO freeswitch;

--
-- Name: sip_shared_appearance_subscriptions; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_shared_appearance_subscriptions (
    subscriber text,
    call_id text,
    aor text,
    profile_name text,
    hostname text,
    contact_str text,
    network_ip text,
    sip_shared_appearance_subscription_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_shared_appearance_subscriptions OWNER TO freeswitch;

--
-- Name: sip_subscriptions; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.sip_subscriptions (
    proto text,
    sip_user text,
    sip_host text,
    sub_to_user text,
    sub_to_host text,
    presence_hosts text,
    event text,
    contact text,
    call_id text,
    full_from text,
    full_via text,
    expires bigint,
    user_agent text,
    accept text,
    profile_name text,
    hostname text,
    network_port text,
    network_ip text,
    version integer DEFAULT 0 NOT NULL,
    orig_proto text,
    full_to text,
    sip_subscription_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.sip_subscriptions OWNER TO freeswitch;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.tasks (
    task_id integer,
    task_desc text,
    task_group text,
    task_runtime bigint,
    task_sql_manager integer,
    hostname text,
    task_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.tasks OWNER TO freeswitch;

--
-- Name: tiers; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.tiers (
   queue text,
   agent text,
   state text,
   level integer DEFAULT 1 NOT NULL,
   "position" integer DEFAULT 1 NOT NULL,
   tier_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.tiers OWNER TO freeswitch;


--
-- Name: json_store; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.json_store (
    name text not null,
    data text,
   json_store_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.json_store OWNER TO freeswitch;


--
-- Name: voicemail_msgs; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.voicemail_msgs (
    created_epoch integer,
    read_epoch    integer,
    username      text,
    domain        text,
    uuid          text,
    cid_name      text,
    cid_number    text,
    in_folder     text,
    file_path     text,
    message_len   integer,
    flags         text,
    read_flags    text,
    forwarded_by  text,
    voicemail_msgs_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.voicemail_msgs OWNER TO freeswitch;


--
-- Name: voicemail_prefs; Type: TABLE; Schema: public; Owner: freeswitch; Tablespace:
--
CREATE TABLE public.voicemail_prefs (
    username        text,
    domain          text,
    name_path       text,
    greeting_path   text,
    password        text,
    voicemail_prefs_uuid uuid PRIMARY KEY default gen_random_uuid()
);
ALTER TABLE public.voicemail_prefs OWNER TO freeswitch;


--Create Views

-- Name: basic_calls; Type: VIEW; Schema: public; Owner: freeswitch

CREATE VIEW public.basic_calls AS
SELECT a.uuid,
   a.direction AS direction,
   a.created AS created,
   a.created_epoch AS created_epoch,
   a.name AS name,
   a.state AS state,
   a.cid_name AS cid_name,
   a.cid_num AS cid_num,
   a.ip_addr AS ip_addr,
   a.dest AS dest,
   a.presence_id AS presence_id,
   a.presence_data AS presence_data,
   a.accountcode AS accountcode,
   a.callstate AS callstate,
   a.callee_name AS callee_name,
   a.callee_num AS callee_num,
   a.callee_direction AS callee_direction,
   a.call_uuid AS call_uuid,
   a.hostname AS hostname,
   a.sent_callee_name AS sent_callee_name,
   a.sent_callee_num AS sent_callee_num,
   b.uuid AS b_uuid,
   b.direction AS b_direction,
   b.created AS b_created,
   b.created_epoch AS b_created_epoch,
   b.name AS b_name,
   b.state AS b_state,
   b.cid_name AS b_cid_name,
   b.cid_num AS b_cid_num,
   b.ip_addr AS b_ip_addr,
   b.dest AS b_dest,
   b.presence_id AS b_presence_id,
   b.presence_data AS b_presence_data,
   b.accountcode AS b_accountcode,
   b.callstate AS b_callstate,
   b.callee_name AS b_callee_name,
   b.callee_num AS b_callee_num,
   b.callee_direction AS b_callee_direction,
   b.sent_callee_name AS b_sent_callee_name,
   b.sent_callee_num AS b_sent_callee_num,
   c.call_created_epoch
  FROM ((public.channels a
    LEFT JOIN public.calls c ON ((((a.uuid)::text = (c.caller_uuid)::text) AND ((a.hostname)::text = (c.hostname)::text))))
    LEFT JOIN public.channels b ON ((((b.uuid)::text = (c.callee_uuid)::text) AND ((b.hostname)::text = (c.hostname)::text))))
 WHERE (((a.uuid)::text = (c.caller_uuid)::text) OR (NOT ((a.uuid)::text IN ( SELECT calls.callee_uuid
          FROM public.calls))));

ALTER TABLE public.basic_calls OWNER TO freeswitch;

-- Name: detailed_calls; Type: VIEW; Schema: public; Owner: freeswitch

CREATE VIEW public.detailed_calls AS
SELECT a.uuid AS uuid,
   a.direction AS direction,
   a.created AS created,
   a.created_epoch AS created_epoch,
   a.name AS name,
   a.state AS state,
   a.cid_name AS cid_name,
   a.cid_num AS cid_num,
   a.ip_addr AS ip_addr,
   a.dest AS dest,
   a.application AS application,
   a.application_data AS application_data,
   a.dialplan AS dialplan,
   a.context AS context,
   a.read_codec AS read_codec,
   a.read_rate AS read_rate,
   a.read_bit_rate AS read_bit_rate,
   a.write_codec AS write_codec,
   a.write_rate AS write_rate,
   a.write_bit_rate AS write_bit_rate,
   a.secure AS secure,
   a.hostname AS hostname,
   a.presence_id AS presence_id,
   a.presence_data AS presence_data,
   a.accountcode AS accountcode,
   a.callstate AS callstate,
   a.callee_name AS callee_name,
   a.callee_num AS callee_num,
   a.callee_direction AS callee_direction,
   a.call_uuid AS call_uuid,
   a.sent_callee_name AS sent_callee_name,
   a.sent_callee_num AS sent_callee_num,
   b.uuid AS b_uuid,
   b.direction AS b_direction,
   b.created AS b_created,
   b.created_epoch AS b_created_epoch,
   b.name AS b_name,
   b.state AS b_state,
   b.cid_name AS b_cid_name,
   b.cid_num AS b_cid_num,
   b.ip_addr AS b_ip_addr,
   b.dest AS b_dest,
   b.application AS b_application,
   b.application_data AS b_application_data,
   b.dialplan AS b_dialplan,
   b.context AS b_context,
   b.read_codec AS b_read_codec,
   b.read_rate AS b_read_rate,
   b.read_bit_rate AS b_read_bit_rate,
   b.write_codec AS b_write_codec,
   b.write_rate AS b_write_rate,
   b.write_bit_rate AS b_write_bit_rate,
   b.secure AS b_secure,
   b.hostname AS b_hostname,
   b.presence_id AS b_presence_id,
   b.presence_data AS b_presence_data,
   b.accountcode AS b_accountcode,
   b.callstate AS b_callstate,
   b.callee_name AS b_callee_name,
   b.callee_num AS b_callee_num,
   b.callee_direction AS b_callee_direction,
   b.call_uuid AS b_call_uuid,
   b.sent_callee_name AS b_sent_callee_name,
   b.sent_callee_num AS b_sent_callee_num,
   c.call_created_epoch
  FROM ((public.channels a
    LEFT JOIN public.calls c ON ((((a.uuid)::text = (c.caller_uuid)::text) AND ((a.hostname)::text = (c.hostname)::text))))
    LEFT JOIN public.channels b ON ((((b.uuid)::text = (c.callee_uuid)::text) AND ((b.hostname)::text = (c.hostname)::text))))
 WHERE (((a.uuid)::text = (c.caller_uuid)::text) OR (NOT ((a.uuid)::text IN ( SELECT calls.callee_uuid
          FROM public.calls))));


ALTER TABLE public.detailed_calls OWNER TO freeswitch;


--Indexes and Constraints

CREATE INDEX alias1 ON public.aliases USING btree (alias);
CREATE INDEX calls1 ON public.calls USING btree (hostname);
CREATE INDEX callsidx1 ON public.calls USING btree (hostname);
CREATE INDEX channels1 ON public.channels USING btree (hostname);
CREATE INDEX chidx1 ON public.channels USING btree (hostname);
CREATE INDEX complete1 ON public.complete USING btree (a1, hostname);
CREATE INDEX complete10 ON public.complete USING btree (a10, hostname);
CREATE INDEX complete11 ON public.complete USING btree (a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, hostname);
CREATE INDEX complete2 ON public.complete USING btree (a2, hostname);
CREATE INDEX complete3 ON public.complete USING btree (a3, hostname);
CREATE INDEX complete4 ON public.complete USING btree (a4, hostname);
CREATE INDEX complete5 ON public.complete USING btree (a5, hostname);
CREATE INDEX complete6 ON public.complete USING btree (a6, hostname);
CREATE INDEX complete7 ON public.complete USING btree (a7, hostname);
CREATE INDEX complete8 ON public.complete USING btree (a8, hostname);
CREATE INDEX complete9 ON public.complete USING btree (a9, hostname);
CREATE UNIQUE INDEX dd_data_key_realm ON public.db_data USING btree (data_key, realm);
CREATE INDEX dd_realm ON public.db_data USING btree (realm);
CREATE INDEX eeuuindex ON public.calls USING btree (callee_uuid);
CREATE INDEX eeuuindex2 ON public.calls USING btree (call_uuid);
CREATE INDEX eruuindex ON public.calls USING btree (caller_uuid, hostname);
CREATE INDEX gd_groupname ON public.group_data USING btree (groupname);
CREATE INDEX gd_url ON public.group_data USING btree (url);
CREATE INDEX ld_hostname ON public.limit_data USING btree (hostname);
CREATE INDEX ld_id ON public.limit_data USING btree (id);
CREATE INDEX ld_realm ON public.limit_data USING btree (realm);
CREATE INDEX ld_uuid ON public.limit_data USING btree (limit_data_uuid);
CREATE INDEX nat_map_port_proto ON public.nat USING btree (port, proto, hostname);
CREATE INDEX recovery1 ON public.recovery USING btree (technology);
CREATE INDEX recovery2 ON public.recovery USING btree (profile_name);
CREATE INDEX recovery3 ON public.recovery USING btree (uuid);
CREATE INDEX regindex1 ON public.registrations USING btree (reg_user, realm, hostname);
CREATE INDEX sa_expires ON public.sip_authentication USING btree (expires);
CREATE INDEX sa_hostname ON public.sip_authentication USING btree (hostname);
CREATE INDEX sa_last_nc ON public.sip_authentication USING btree (last_nc);
CREATE INDEX sa_nonce ON public.sip_authentication USING btree (nonce);
CREATE INDEX sd_call_id ON public.sip_dialogs USING btree (call_id);
CREATE INDEX sd_call_info ON public.sip_dialogs USING btree (call_info);
CREATE INDEX sd_call_info_state ON public.sip_dialogs USING btree (call_info_state);
CREATE INDEX sd_expires ON public.sip_dialogs USING btree (expires);
CREATE INDEX sd_hostname ON public.sip_dialogs USING btree (hostname);
CREATE INDEX sd_presence_data ON public.sip_dialogs USING btree (presence_data);
CREATE INDEX sd_presence_id ON public.sip_dialogs USING btree (presence_id);
CREATE INDEX sd_rcd ON public.sip_dialogs USING btree (rcd);
CREATE INDEX sd_sip_from_host ON public.sip_dialogs USING btree (sip_from_host);
CREATE INDEX sd_sip_from_tag ON public.sip_dialogs USING btree (sip_from_tag);
CREATE INDEX sd_sip_from_user ON public.sip_dialogs USING btree (sip_from_user);
CREATE INDEX sd_sip_to_host ON public.sip_dialogs USING btree (sip_to_host);
CREATE INDEX sd_sip_to_tag ON public.sip_dialogs USING btree (sip_to_tag);
CREATE INDEX sd_uuid ON public.sip_dialogs USING btree (uuid);
CREATE INDEX sp_expires ON public.sip_presence USING btree (expires);
CREATE INDEX sp_hostname ON public.sip_presence USING btree (hostname);
CREATE INDEX sp_open_closed ON public.sip_presence USING btree (open_closed);
CREATE INDEX sp_profile_name ON public.sip_presence USING btree (profile_name);
CREATE INDEX sp_sip_host ON public.sip_presence USING btree (sip_host);
CREATE INDEX sp_sip_user ON public.sip_presence USING btree (sip_user);
CREATE INDEX sr_call_id ON public.sip_registrations USING btree (call_id);
CREATE INDEX sr_contact ON public.sip_registrations USING btree (contact);
CREATE INDEX sr_expires ON public.sip_registrations USING btree (expires);
CREATE INDEX sr_hostname ON public.sip_registrations USING btree (hostname);
CREATE INDEX sr_mwi_host ON public.sip_registrations USING btree (mwi_host);
CREATE INDEX sr_mwi_user ON public.sip_registrations USING btree (mwi_user);
CREATE INDEX sr_network_ip ON public.sip_registrations USING btree (network_ip);
CREATE INDEX sr_network_port ON public.sip_registrations USING btree (network_port);
CREATE INDEX sr_orig_hostname ON public.sip_registrations USING btree (orig_hostname);
CREATE INDEX sr_orig_server_host ON public.sip_registrations USING btree (orig_server_host);
CREATE INDEX sr_ping_expires ON public.sip_registrations USING btree (ping_expires);
CREATE INDEX sr_ping_status ON public.sip_registrations USING btree (ping_status);
CREATE INDEX sr_presence_hosts ON public.sip_registrations USING btree (presence_hosts);
CREATE INDEX sr_profile_name ON public.sip_registrations USING btree (profile_name);
CREATE INDEX sr_sip_host ON public.sip_registrations USING btree (sip_host);
CREATE INDEX sr_sip_realm ON public.sip_registrations USING btree (sip_realm);
CREATE INDEX sr_sip_user ON public.sip_registrations USING btree (sip_user);
CREATE INDEX sr_sip_username ON public.sip_registrations USING btree (sip_username);
CREATE INDEX sr_status ON public.sip_registrations USING btree (status);
CREATE INDEX sr_sub_host ON public.sip_registrations USING btree (sub_host);
CREATE INDEX ss_call_id ON public.sip_subscriptions USING btree (call_id);
CREATE INDEX ss_contact ON public.sip_subscriptions USING btree (contact);
CREATE INDEX ss_event ON public.sip_subscriptions USING btree (event);
CREATE INDEX ss_expires ON public.sip_subscriptions USING btree (expires);
CREATE INDEX ss_full_from ON public.sip_subscriptions USING btree (full_from);
CREATE INDEX ss_hostname ON public.sip_subscriptions USING btree (hostname);
CREATE INDEX ss_multi ON public.sip_subscriptions USING btree (call_id, profile_name, hostname);
CREATE INDEX ss_network_ip ON public.sip_subscriptions USING btree (network_ip);
CREATE INDEX ss_network_port ON public.sip_subscriptions USING btree (network_port);
CREATE INDEX ss_orig_proto ON public.sip_subscriptions USING btree (orig_proto);
CREATE INDEX ss_presence_hosts ON public.sip_subscriptions USING btree (presence_hosts);
CREATE INDEX ss_profile_name ON public.sip_subscriptions USING btree (profile_name);
CREATE INDEX ss_proto ON public.sip_subscriptions USING btree (proto);
CREATE INDEX ss_sip_host ON public.sip_subscriptions USING btree (sip_host);
CREATE INDEX ss_sip_user ON public.sip_subscriptions USING btree (sip_user);
CREATE INDEX ss_sub_to_host ON public.sip_subscriptions USING btree (sub_to_host);
CREATE INDEX ss_sub_to_user ON public.sip_subscriptions USING btree (sub_to_user);
CREATE INDEX ss_version ON public.sip_subscriptions USING btree (version);
CREATE INDEX ssa_aor ON public.sip_shared_appearance_subscriptions USING btree (aor);
CREATE INDEX ssa_hostname ON public.sip_shared_appearance_subscriptions USING btree (hostname);
CREATE INDEX ssa_network_ip ON public.sip_shared_appearance_subscriptions USING btree (network_ip);
CREATE INDEX ssa_profile_name ON public.sip_shared_appearance_subscriptions USING btree (profile_name);
CREATE INDEX ssa_subscriber ON public.sip_shared_appearance_subscriptions USING btree (subscriber);
CREATE INDEX ssd_call_id ON public.sip_shared_appearance_dialogs USING btree (call_id);
CREATE INDEX ssd_contact_str ON public.sip_shared_appearance_dialogs USING btree (contact_str);
CREATE INDEX ssd_expires ON public.sip_shared_appearance_dialogs USING btree (expires);
CREATE INDEX ssd_hostname ON public.sip_shared_appearance_dialogs USING btree (hostname);
CREATE INDEX ssd_profile_name ON public.sip_shared_appearance_dialogs USING btree (profile_name);
CREATE INDEX tasks1 ON public.tasks USING btree (hostname, task_id);
CREATE INDEX uuindex ON public.channels USING btree (uuid, hostname);
CREATE INDEX uuindex2 ON public.channels USING btree (call_uuid);
CREATE INDEX voicemail_msgs_idx1 on public.voicemail_msgs USING btree (created_epoch);
CREATE INDEX voicemail_msgs_idx2 on public.voicemail_msgs USING btree (username);
CREATE INDEX voicemail_msgs_idx3 on public.voicemail_msgs USING btree (domain);
CREATE INDEX voicemail_msgs_idx4 on public.voicemail_msgs USING btree (uuid);
CREATE INDEX voicemail_msgs_idx5 on public.voicemail_msgs USING btree (in_folder);
CREATE INDEX voicemail_msgs_idx6 on public.voicemail_msgs USING btree (read_flags);
CREATE INDEX voicemail_msgs_idx7 on public.voicemail_msgs USING btree (forwarded_by);
CREATE INDEX voicemail_msgs_idx8 on public.voicemail_msgs USING btree (read_epoch);
CREATE INDEX voicemail_msgs_idx9 on public.voicemail_msgs USING btree (flags);
CREATE INDEX voicemail_prefs_idx1 on public.voicemail_prefs USING btree (username);
CREATE INDEX voicemail_prefs_idx2 on public.voicemail_prefs USING btree (domain);
