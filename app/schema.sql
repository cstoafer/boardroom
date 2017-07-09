drop table if exists issuer;
create table issuer (
    cik     integer primary key,
    name    text not null,
    ticker  text not null
);

drop table if exists insider;
create table insider (
    cik                   integer primary key,
    name                  text not null,
    addr1                 text not null,
    addr2                 text not null,
    city                  text not null,
    state                 text not null,
    zipcode               text not null,
    is_officer            text,
    is_director           text,
    is_ten_percent_owner  text,
    is_other_exec_type    text,
);

drop table if exists trade;
create table trade (
    id                      integer primary key autoincrement,
    date                    text not null,
    num_shares              real not null,
    price_per_share         real not null,
    sec_type                text not null,
    direct_or_indirect      text not null,
    acquired_disposed_code  text not null,
    transaction_code        text not null,
    shares_owned_after      real not null,
    issuer_cik              integer not NULL,
    insider_cik             integer not NULL,
      foreign key (issuer_cik) references issuer(cik),
      foreign key (insider_cik) references insider(cik)
);

