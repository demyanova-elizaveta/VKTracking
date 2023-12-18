CREATE TABLE profilesPosts (
 profile_id integer,
 post_id integer,
 post_date date,
 refreshed_date date,
 is_deleted integer CHECK(is_deleted = 0 or is_deleted = 1),
 post_theme text,
 primary key(profile_id, post_id)
);

CREATE TABLE communitiesPosts (
 community_id integer,
 post_id integer,
 post_date date,
 refreshed_date date,
 is_deleted integer CHECK(is_deleted = 0 or is_deleted = 1),
 post_theme text,
 primary key(community_id, post_id)
);

create table communitiesLikes (
 community_id integer,
 post_id integer,
 user_id text,
 refreshed_date date,
 primary key(community_id, post_id, user_id),
 foreign key(community_id, post_id) references communitiesPosts(community_id, post_id)
);

create table profilesLikes (
 profile_id integer,
 post_id integer,
 user_id text,
 refreshed_date date,
 primary key(profile_id, post_id, user_id),
 foreign key(profile_id, post_id) references profilesPosts(profile_id, post_id)
);

create table communitiesComments (
 community_id integer,
 post_id integer,
 user_id text,
 comment_id integer,
 comment_date date,
 parent_id integer,
 refreshed_date date,
 comment_text text,
 primary key(community_id, post_id, comment_id),
 foreign key(community_id, post_id) references communitiesPosts(community_id, post_id)
);

create table profilesComments (
 profile_id integer,
 post_id integer,
 user_id text,
 comment_id integer,
 comment_date date,
 parent_id integer,
 refreshed_date date,
 primary key(profile_id, post_id, comment_id),
 foreign key(profile_id, post_id) references profilesPosts(profile_id, post_id)
);



