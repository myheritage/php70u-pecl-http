%global pecl_name http
%global php_base php70u
%global ini_name  40-%{pecl_name}.ini
%global with_zts 0%{?__ztsphp:1}

Summary: Extended HTTP support
Name: %{php_base}-pecl-%{pecl_name}
Version: 3.0.1
Release: 1.MyHeritage.ius%{?dist}
License: ASL 2.0
Group: Development/Libraries
%if 0%{?gh_commit:1}
Source0:      https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{version}%{?prever}.tar.gz
%else
Source0:       http://pecl.php.net/get/pecl_%{pecl_name}-%{version}%{?prever}.tgz
%endif
Source1: %{pecl_name}.ini
URL: http://pecl.php.net/package/%{pecl_name}
BuildRequires: %{php_base}-pear
BuildRequires: %{php_base}-devel
BuildRequires: %{php_base}-hash
BuildRequires: %{php_base}-iconv
BuildRequires: %{php_base}-spl
BuildRequires: %{php_base}-pecl-propro-devel >= 1.0.0
BuildRequires: %{php_base}-pecl-raphf-devel  >= 1.1.0
# https://pecl.php.net/package-info.php?package=http&version=3.4.0RC2
BuildRequires: pcre-devel
BuildRequires: zlib-devel >= 1.2.0.4
BuildRequires: curl-devel >= 7.18.2
BuildRequires: libidn-devel
BuildRequires: libevent-devel  > 2
%if 0%{?fedora} < 24
Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
%endif
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
Requires: libevent%{_isa} > 2
Requires: libcurl%{_isa}
Requires: zlib%{_isa}
Requires: %{php_base}-hash%{?_isa}
Requires: %{php_base}-iconv%{?_isa}
Requires: %{php_base}-spl%{?_isa}
Requires: %{php_base}-pecl(propro)%{?_isa} >= 1.0.0
Requires: %{php_base}-pecl(raphf)%{?_isa}  >= 1.1.0
# provide the stock name
Provides: php-pecl-%{pecl_name} = %{version}
Provides: php-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides: php-%{pecl_name} = %{version}
Provides: php-%{pecl_name}%{?_isa} = %{version}
Provides: %{php_base}-%{pecl_name} = %{version}
Provides: %{php_base}-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides: php-pecl(%{pecl_name}) = %{version}
Provides: php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides: %{php_base}-pecl(%{pecl_name}) = %{version}
Provides: %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts: php-pecl-%{pecl_name} < %{version}

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
The HTTP extension aims to provide a convenient and powerful set of
functionality for major applications.

The HTTP extension eases handling of HTTP URLs, dates, redirects, headers
and messages in a HTTP context (both incoming and outgoing). It also provides
means for client negotiation of preferred language and charset, as well as
a convenient way to exchange arbitrary data with caching and resuming
capabilities.

Also provided is a powerful request and parallel interface.

Version 2 is completely incompatible to previous version.

Note:
. php-pecl-http1 provides API version 1
. php-pecl-http  provides API version 2

Documentation : http://devel-m6w6.rhcloud.com/mdref/http


%package devel
Summary:       Extended HTTP support developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{php_base}-devel%{?_isa} >= 5.3.0
Provides:      %{php_base}-pecl-%{pecl_name}-devel          = %{version}%{?prever}
Provides:      %{php_base}-pecl-%{pecl_name}-devel%{?_isa}  = %{version}%{?prever}

%description devel
These are the files needed to compile programs using HTTP extension.


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

%if %{with_zts}
cp -r NTS ZTS
%endif


%build
pushd NTS
phpize
%{configure} --with-%{pecl_name}=%{prefix} --with-php-config=%{_bindir}/php-config
%{__make}
popd

%if %{with_zts}
pushd ZTS
zts-phpize
%{configure} --with-%{pecl_name}=%{prefix} --with-php-config=%{_bindir}/zts-php-config
%{__make}
popd
%endif


%install
%{__make} install INSTALL_ROOT=%{buildroot} -C NTS

# Install XML package description
install -Dpm 0644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

# Install config file
install -Dpm 0644 %{SOURCE1} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
%{__make} install INSTALL_ROOT=%{buildroot} -C ZTS

# Install config file
install -Dpm 0644 %{SOURCE1} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

rm -rf %{buildroot}%{php_incldir}/ext/%{pecl_name}/
%if %{with_zts}
rm -rf %{buildroot}%{php_ztsincldir}/ext/%{pecl_name}/
%endif

# Documentation
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
# simple module load test
%{__php} \
    --no-php-ini \
    --define extension_dir=%{buildroot}%{php_extdir} \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}
%if %{with_zts}
%{__ztsphp} \
    --no-php-ini \
    --define extension_dir=%{buildroot}%{php_ztsextdir} \
    --define extension=%{pecl_name}.so \
    --modules | grep %{pecl_name}
%endif


%if 0%{?fedora} < 24
%post
%if 0%{?pecl_install:1}
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml
%endif


%postun
%if 0%{?pecl_uninstall:1}
if [ "$1" -eq "0" ]; then
%{pecl_uninstall} %{pecl_name}
fi
%endif
%endif


%files
%doc %{pecl_docdir}/%{pecl_name}
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{pecl_name}.xml
%config(noreplace) %verify(not md5 mtime size) %{php_inidir}/%{ini_name}

%if %{with_zts}
%{php_ztsextdir}/%{pecl_name}.so
%config(noreplace) %verify(not md5 mtime size) %{php_ztsinidir}/%{ini_name}
%endif

%files devel
%defattr(-,root,root,-)
%doc %{pecl_testdir}/%{proj_name}
%{php_incldir}/ext/%{pecl_name}

%if %{with_zts}
%{php_ztsincldir}/ext/%{pecl_name}
%endif

%changelog
